#!/usr/bin/env python3
"""
QNG-T-TRJ-CTRL-001

Adversarial anti-shortcut controls for trajectory:
- orientation permutation control,
- segment-scale permutation control,
- directional sign-randomization collapse,
- symmetric/control amplitude sanity.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import math
import random
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FLYBY_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
DEFAULT_PIONEER_CSV = ROOT / "data" / "trajectory" / "pioneer_ds005_anchor.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-trj-ctrl-001"


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
    p = argparse.ArgumentParser(description="Run QNG-T-TRJ-CTRL-001.")
    p.add_argument("--test-id", default="QNG-T-TRJ-CTRL-001")
    p.add_argument("--dataset-id", default="DS-005")
    p.add_argument("--flyby-csv", default=str(DEFAULT_FLYBY_CSV))
    p.add_argument("--use-pioneer-anchor", action="store_true")
    p.add_argument("--pioneer-csv", default=str(DEFAULT_PIONEER_CSV))
    p.add_argument("--n-runs", type=int, default=1200)
    p.add_argument("--seed", type=int, default=20260221)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


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

    perigee, _, mixed, _ = tr.build_observations(rows)
    if args.use_pioneer_anchor:
        pioneer_csv = Path(args.pioneer_csv)
        if not pioneer_csv.is_absolute():
            pioneer_csv = (ROOT / pioneer_csv).resolve()
        p_rows, p_warnings = tr.parse_pioneer_csv(pioneer_csv)
        warnings.extend(p_warnings)
        p_perigee, _, p_mixed, _, _ = tr.build_pioneer_observations(p_rows)
        perigee.extend(p_perigee)
        mixed.extend(p_mixed)

    science = [o for o in perigee if not (o.is_control or o.is_symmetric)]
    mixed_science = [o for o in mixed if not (o.is_control or o.is_symmetric)]
    science_flyby = [o for o in science if o.data_domain == "flyby_real"]
    mixed_science_flyby = [o for o in mixed_science if o.data_domain == "flyby_real"]
    controls = [o for o in perigee if (o.is_control or o.is_symmetric)]
    if len(science) < 5:
        raise RuntimeError(f"Need >=5 science rows for adversarial controls; got {len(science)}.")
    if len(mixed_science) < 8:
        raise RuntimeError(f"Need >=8 mixed science rows for segment control; got {len(mixed_science)}.")

    shuffle_perigee = (
        science_flyby if (args.use_pioneer_anchor and len(science_flyby) >= 3) else science
    )
    shuffle_mixed = (
        mixed_science_flyby if (args.use_pioneer_anchor and len(mixed_science_flyby) >= 6) else mixed_science
    )

    base_fit = tr.fit(science)
    base_fit_shuffle_perigee = tr.fit(shuffle_perigee)
    base_fit_shuffle_mixed = tr.fit(shuffle_mixed)

    rng = random.Random(args.seed)
    n_runs = max(300, args.n_runs)

    # C1: orientation permutation control.
    orient_vals: list[float] = []
    x_base = [o.x for o in shuffle_perigee]
    for _ in range(n_runs):
        x_perm = x_base[:]
        rng.shuffle(x_perm)
        orient_vals.append(tr.fit(shuffle_perigee, x_perm).dchi2)
    orient_med = statistics.median(orient_vals)
    orient_target = base_fit_shuffle_perigee.dchi2
    orient_p = sum(1 for v in orient_vals if v <= orient_target) / float(len(orient_vals))
    orient_ratio = abs(orient_med) / max(abs(orient_target), 1e-30)

    # C2: segment-scale permutation control on mixed series.
    seg_vals: list[float] = []
    scales = [o.scale for o in shuffle_mixed]
    for _ in range(n_runs):
        s_perm = scales[:]
        rng.shuffle(s_perm)
        x_perm = [o.base_x * s for o, s in zip(shuffle_mixed, s_perm)]
        seg_vals.append(tr.fit(shuffle_mixed, x_perm).dchi2)
    seg_med = statistics.median(seg_vals)
    seg_target = base_fit_shuffle_mixed.dchi2
    seg_p = sum(1 for v in seg_vals if v <= seg_target) / float(len(seg_vals))
    seg_ratio = abs(seg_med) / max(abs(seg_target), 1e-30)

    # C3: sign-randomization collapse of directionality.
    dir_vals: list[float] = []
    for _ in range(n_runs):
        x_flip = [(-o.x if rng.random() < 0.5 else o.x) for o in science]
        dir_vals.append(tr.fit(science, x_flip).directionality)
    dir_median = statistics.median(dir_vals)
    dir_tail_p = sum(1 for v in dir_vals if v >= base_fit.directionality) / float(len(dir_vals))

    # C4: symmetric/control rows should stay near zero.
    control_z_mean = (
        statistics.fmean(abs(o.y) / max(o.sigma, 1e-30) for o in controls) if controls else 0.0
    )

    gates = {
        "C1_orientation_permutation": (orient_p <= 0.10) and (orient_ratio <= 0.45),
        "C2_segment_permutation": (seg_p <= 0.10) and (seg_ratio <= 0.95),
        "C3_directionality_collapse": (dir_median <= 0.60) and (dir_tail_p <= 0.10),
        "C4_control_zero": control_z_mean <= 1.50,
    }
    decision = "pass" if all(gates.values()) else "fail"

    write_key_value_csv(
        out_dir / "fit-summary.csv",
        {
            "test_id": args.test_id,
            "dataset_id": args.dataset_id,
            "decision": decision,
            "n_science": str(len(science)),
            "n_mixed_science": str(len(mixed_science)),
            "n_controls": str(len(controls)),
            "base_delta_chi2": fmt(base_fit.dchi2),
            "base_directionality": fmt(base_fit.directionality),
            "base_shuffle_perigee_delta_chi2": fmt(base_fit_shuffle_perigee.dchi2),
            "base_shuffle_mixed_delta_chi2": fmt(base_fit_shuffle_mixed.dchi2),
            "orientation_median_delta_chi2": fmt(orient_med),
            "orientation_p_value": fmt(orient_p),
            "orientation_ratio_vs_real": fmt(orient_ratio),
            "segment_median_delta_chi2": fmt(seg_med),
            "segment_p_value": fmt(seg_p),
            "segment_ratio_vs_real": fmt(seg_ratio),
            "directionality_randomized_median": fmt(dir_median),
            "directionality_tail_p": fmt(dir_tail_p),
            "control_mean_abs_over_sigma": fmt(control_z_mean),
            "rule_pass_C1_orientation_permutation": str(gates["C1_orientation_permutation"]),
            "rule_pass_C2_segment_permutation": str(gates["C2_segment_permutation"]),
            "rule_pass_C3_directionality_collapse": str(gates["C3_directionality_collapse"]),
            "rule_pass_C4_control_zero": str(gates["C4_control_zero"]),
        },
    )

    write_key_value_csv(
        out_dir / "anti_shortcut_summary.csv",
        {
            "n_runs": str(n_runs),
            "orientation_median_delta_chi2": fmt(orient_med),
            "orientation_p_value": fmt(orient_p),
            "orientation_ratio_vs_real": fmt(orient_ratio),
            "segment_median_delta_chi2": fmt(seg_med),
            "segment_p_value": fmt(seg_p),
            "segment_ratio_vs_real": fmt(seg_ratio),
            "directionality_base": fmt(base_fit.directionality),
            "directionality_randomized_median": fmt(dir_median),
            "directionality_tail_p": fmt(dir_tail_p),
            "control_mean_abs_over_sigma": fmt(control_z_mean),
        },
    )

    write_md(
        out_dir / "anti_shortcut_report.md",
        [
            "# Trajectory Adversarial Anti-Shortcut",
            "",
            f"- decision: `{decision}`",
            f"- n_science: `{len(science)}`",
            f"- base_delta_chi2: `{fmt(base_fit.dchi2)}`",
            f"- base_directionality: `{fmt(base_fit.directionality)}`",
            "",
            "## Controls",
            f"- C1 orientation permutation: median dchi2=`{fmt(orient_med)}`, p=`{fmt(orient_p)}`, ratio=`{fmt(orient_ratio)}`",
            f"- C2 segment permutation: median dchi2=`{fmt(seg_med)}`, p=`{fmt(seg_p)}`, ratio=`{fmt(seg_ratio)}`",
            f"- C3 directionality collapse: randomized median=`{fmt(dir_median)}`, tail p=`{fmt(dir_tail_p)}`",
            f"- C4 symmetric/control zero: mean |a|/sigma=`{fmt(control_z_mean)}`",
            "",
            "## Gates",
            f"- C1: `{'pass' if gates['C1_orientation_permutation'] else 'fail'}`",
            f"- C2: `{'pass' if gates['C2_segment_permutation'] else 'fail'}`",
            f"- C3: `{'pass' if gates['C3_directionality_collapse'] else 'fail'}`",
            f"- C4: `{'pass' if gates['C4_control_zero'] else 'fail'}`",
        ],
    )

    run_log = [
        "QNG-T-TRJ-CTRL-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_id: {args.dataset_id}",
        f"flyby_csv: {flyby_csv}",
        f"use_pioneer_anchor: {args.use_pioneer_anchor}",
        f"pioneer_csv: {args.pioneer_csv}",
        f"n_runs: {n_runs}",
        f"seed: {args.seed}",
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
        f"QNG trajectory anti-shortcut run complete: decision={decision} "
        f"orient_p={fmt(orient_p)} seg_p={fmt(seg_p)} dir_med={fmt(dir_median)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
