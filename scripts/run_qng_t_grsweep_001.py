#!/usr/bin/env python3
"""
QNG-T-GRSWEEP-001

Hard GR kill-switch test:
Sweep tau from 0 to tau_hat and verify
- monotonic signal activation on science rows,
- strong endpoint improvement vs baseline,
- clean controls (small relative response).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import math
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FLYBY_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
DEFAULT_PIONEER_CSV = ROOT / "data" / "trajectory" / "pioneer_ds005_anchor.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-grsweep-001"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0.0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_key_value_csv(path: Path, payload: dict[str, str]) -> None:
    write_csv(path, ["metric", "value"], [{"metric": k, "value": v} for k, v in payload.items()])


def write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-GRSWEEP-001.")
    p.add_argument("--test-id", default="QNG-T-GRSWEEP-001")
    p.add_argument("--dataset-id", default="DS-005")
    p.add_argument("--flyby-csv", default=str(DEFAULT_FLYBY_CSV))
    p.add_argument("--use-pioneer-anchor", action="store_true")
    p.add_argument("--pioneer-csv", default=str(DEFAULT_PIONEER_CSV))
    p.add_argument("--n-steps", type=int, default=10, help="Produces n_steps+1 points from 0..1.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def chi2_for_tau(obs, tau: float) -> float:
    total = 0.0
    for o in obs:
        resid = o.y - tau * o.x
        total += (resid * resid) / max(o.sigma * o.sigma, 1e-30)
    return total


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.append(str((ROOT / "scripts").resolve()))
    import run_qng_t_028_trajectory_real as tr  # type: ignore

    t0 = time.perf_counter()
    warnings: list[str] = []

    flyby_csv = Path(args.flyby_csv)
    if not flyby_csv.is_absolute():
        flyby_csv = (ROOT / flyby_csv).resolve()
    rows, row_warnings = tr.parse_real_csv(flyby_csv)
    warnings.extend(row_warnings)

    perigee, _, _, _ = tr.build_observations(rows)
    if args.use_pioneer_anchor:
        pioneer_csv = Path(args.pioneer_csv)
        if not pioneer_csv.is_absolute():
            pioneer_csv = (ROOT / pioneer_csv).resolve()
        p_rows, p_warnings = tr.parse_pioneer_csv(pioneer_csv)
        warnings.extend(p_warnings)
        p_perigee, _, _, _, _ = tr.build_pioneer_observations(p_rows)
        perigee.extend(p_perigee)

    science = [o for o in perigee if not (o.is_control or o.is_symmetric)]
    controls = [o for o in perigee if (o.is_control or o.is_symmetric)]
    if len(science) < 4:
        raise RuntimeError(f"Need >=4 science rows for tau sweep; got {len(science)}.")

    fit = tr.fit(science)
    tau_hat = fit.tau
    n_steps = max(4, int(args.n_steps))
    alphas = [i / n_steps for i in range(n_steps + 1)]

    sweep_rows: list[dict[str, str]] = []
    chi_science: list[float] = []
    chi_control: list[float] = []
    for a in alphas:
        tau = a * tau_hat
        cs = chi2_for_tau(science, tau)
        cc = chi2_for_tau(controls, tau) if controls else 0.0
        chi_science.append(cs)
        chi_control.append(cc)
        sweep_rows.append(
            {
                "alpha": fmt(a),
                "tau": fmt(tau),
                "chi2_science": fmt(cs),
                "chi2_control": fmt(cc),
            }
        )

    base_science = chi_science[0]
    end_science = chi_science[-1]
    delta_science = end_science - base_science
    base_control = chi_control[0]
    end_control = chi_control[-1]
    delta_control = end_control - base_control

    monotonic = all(chi_science[i] <= chi_science[i - 1] + 1e-9 for i in range(1, len(chi_science)))
    control_ratio = abs(delta_control) / max(abs(delta_science), 1e-30)

    gates = {
        "S1_monotonic_activation": monotonic,
        "S2_endpoint_signal_strength": delta_science <= -1000.0,
        "S3_control_clean_ratio": control_ratio <= 0.05,
    }
    decision = "pass" if all(gates.values()) else "fail"

    write_csv(out_dir / "tau_sweep.csv", list(sweep_rows[0].keys()), sweep_rows)
    write_key_value_csv(
        out_dir / "fit-summary.csv",
        {
            "test_id": args.test_id,
            "dataset_id": args.dataset_id,
            "decision": decision,
            "n_science": str(len(science)),
            "n_controls": str(len(controls)),
            "tau_hat": fmt(tau_hat),
            "chi2_science_alpha0": fmt(base_science),
            "chi2_science_alpha1": fmt(end_science),
            "delta_chi2_science_alpha1_minus_alpha0": fmt(delta_science),
            "chi2_control_alpha0": fmt(base_control),
            "chi2_control_alpha1": fmt(end_control),
            "delta_chi2_control_alpha1_minus_alpha0": fmt(delta_control),
            "control_delta_ratio_vs_science": fmt(control_ratio),
            "rule_pass_S1_monotonic_activation": str(gates["S1_monotonic_activation"]),
            "rule_pass_S2_endpoint_signal_strength": str(gates["S2_endpoint_signal_strength"]),
            "rule_pass_S3_control_clean_ratio": str(gates["S3_control_clean_ratio"]),
        },
    )

    write_md(
        out_dir / "gr-killswitch-report.md",
        [
            "# Tau->0 GR Kill-Switch",
            "",
            f"- decision: `{decision}`",
            f"- tau_hat: `{fmt(tau_hat)}`",
            f"- n_science: `{len(science)}`",
            f"- n_controls: `{len(controls)}`",
            f"- delta_chi2_science(alpha=1 - alpha=0): `{fmt(delta_science)}`",
            f"- delta_chi2_control(alpha=1 - alpha=0): `{fmt(delta_control)}`",
            f"- control_ratio: `{fmt(control_ratio)}`",
            "",
            "## Gates",
            f"- S1 monotonic activation: `{'pass' if gates['S1_monotonic_activation'] else 'fail'}`",
            f"- S2 endpoint signal strength: `{'pass' if gates['S2_endpoint_signal_strength'] else 'fail'}`",
            f"- S3 control clean ratio: `{'pass' if gates['S3_control_clean_ratio'] else 'fail'}`",
        ],
    )

    run_log = [
        "QNG-T-GRSWEEP-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_id: {args.dataset_id}",
        f"flyby_csv: {flyby_csv}",
        f"use_pioneer_anchor: {args.use_pioneer_anchor}",
        f"pioneer_csv: {args.pioneer_csv}",
        f"n_steps: {n_steps}",
        f"duration_seconds: {fmt(time.perf_counter() - t0)}",
        f"decision: {decision}",
        "",
    ]
    if warnings:
        run_log.append("warnings:")
        for w in warnings:
            run_log.append(f"- {w}")
    write_md(out_dir / "run-log.txt", run_log)

    print(
        f"QNG GR-sweep run complete: decision={decision} "
        f"tau_hat={fmt(tau_hat)} delta_science={fmt(delta_science)} control_ratio={fmt(control_ratio)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

