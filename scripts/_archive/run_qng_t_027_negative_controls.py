#!/usr/bin/env python3
"""
Negative-control diagnostics for QNG-T-027 lensing/rotation workflow.

This script uses the same parsed inputs as run_qng_t_027_lensing_dark.py and evaluates:
- positive fit improvements (lensing + rotation)
- lensing permutation control (shuffle gradients)
- rotation permutation control (shuffle history terms)

Outputs in --out-dir:
- negative-controls-summary.csv
- negative-controls-runs.csv
- negative-controls.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import random
import statistics
import sys


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_qng_t_027_lensing_dark as q027


@dataclass
class ControlRun:
    mode: str
    seed: int
    delta_chi2_lens: float
    delta_chi2_rot: float
    delta_chi2_total: float
    delta_aic_total: float


def fit_components(
    lensing: list[q027.LensingPoint],
    rotation: list[q027.RotationPoint],
) -> tuple[float, float, float, float, float, float, float]:
    tau_fit, chi2_lens_mem = q027.fit_tau(lensing)
    chi2_lens_base = q027.chi2_lensing(lensing, tau=0.0)
    k_fit, chi2_rot_mem = q027.fit_k(rotation)
    chi2_rot_base = q027.chi2_rotation(rotation, k=0.0)

    d_lens = chi2_lens_mem - chi2_lens_base
    d_rot = chi2_rot_mem - chi2_rot_base
    d_total = d_lens + d_rot
    d_aic = (chi2_lens_mem + chi2_rot_mem + 2 * 2) - (chi2_lens_base + chi2_rot_base)
    return tau_fit, k_fit, d_lens, d_rot, d_total, d_aic, q027.offset_score(lensing, tau_fit)


def shuffled_lensing(
    lensing: list[q027.LensingPoint],
    rng: random.Random,
) -> list[q027.LensingPoint]:
    grads = [(p.grad_dx, p.grad_dy) for p in lensing]
    rng.shuffle(grads)
    out: list[q027.LensingPoint] = []
    for p, (gx, gy) in zip(lensing, grads):
        out.append(
            q027.LensingPoint(
                system_id=p.system_id,
                obs_dx=p.obs_dx,
                obs_dy=p.obs_dy,
                grad_dx=gx,
                grad_dy=gy,
                sigma=p.sigma,
            )
        )
    return out


def shuffled_rotation(
    rotation: list[q027.RotationPoint],
    rng: random.Random,
) -> list[q027.RotationPoint]:
    h = [p.history_term for p in rotation]
    rng.shuffle(h)
    out: list[q027.RotationPoint] = []
    for p, hh in zip(rotation, h):
        out.append(
            q027.RotationPoint(
                system_id=p.system_id,
                radius=p.radius,
                v_obs=p.v_obs,
                v_err=p.v_err,
                baryon_term=p.baryon_term,
                history_term=hh,
            )
        )
    return out


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    return statistics.median(values)


def fmt(v: float) -> str:
    return q027.fmt(v)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run negative-control diagnostics for DS-006 lensing/rotation fits.")
    p.add_argument("--test-id", default=q027.DEFAULT_TEST_ID, help="Logical test ID label used in report headers.")
    p.add_argument("--lensing-csv", required=True, help="Path to lensing CSV.")
    p.add_argument("--rotation-csv", required=True, help="Path to rotation CSV.")
    p.add_argument("--out-dir", default="05_validation/evidence/artifacts/qng-t-027", help="Output directory.")
    p.add_argument("--n-runs", type=int, default=24, help="Number of permutation runs per control.")
    p.add_argument("--seed", type=int, default=97, help="Random seed for control permutations.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    lensing, lw = q027.parse_lensing_csv(Path(args.lensing_csv))
    rotation, rw = q027.parse_rotation_csv(Path(args.rotation_csv))

    tau, k_mem, d_lens_pos, d_rot_pos, d_total_pos, d_aic_pos, offset_pos = fit_components(lensing, rotation)

    runs: list[ControlRun] = []
    rng = random.Random(args.seed)

    for i in range(max(1, args.n_runs)):
        rr = random.Random(rng.randint(1, 10_000_000))
        l_shuf = shuffled_lensing(lensing, rr)
        _, _, d_lens, d_rot, d_total, d_aic, _ = fit_components(l_shuf, rotation)
        runs.append(
            ControlRun(
                mode="lensing_shuffle",
                seed=i,
                delta_chi2_lens=d_lens,
                delta_chi2_rot=d_rot,
                delta_chi2_total=d_total,
                delta_aic_total=d_aic,
            )
        )

    for i in range(max(1, args.n_runs)):
        rr = random.Random(rng.randint(1, 10_000_000))
        r_shuf = shuffled_rotation(rotation, rr)
        _, _, d_lens, d_rot, d_total, d_aic, _ = fit_components(lensing, r_shuf)
        runs.append(
            ControlRun(
                mode="rotation_shuffle",
                seed=i,
                delta_chi2_lens=d_lens,
                delta_chi2_rot=d_rot,
                delta_chi2_total=d_total,
                delta_aic_total=d_aic,
            )
        )

    lens_ctrl = [r for r in runs if r.mode == "lensing_shuffle"]
    rot_ctrl = [r for r in runs if r.mode == "rotation_shuffle"]

    lens_improve_pos = -d_lens_pos
    rot_improve_pos = -d_rot_pos
    lens_improve_ctrl_med = -median([r.delta_chi2_lens for r in lens_ctrl])
    rot_improve_ctrl_med = -median([r.delta_chi2_rot for r in rot_ctrl])

    lens_ratio = lens_improve_ctrl_med / max(lens_improve_pos, 1e-12)
    rot_ratio = rot_improve_ctrl_med / max(rot_improve_pos, 1e-12)

    lens_gate = lens_ratio <= 0.20
    rot_gate = rot_ratio <= 0.20
    neg_control_pass = lens_gate and rot_gate

    summary_path = out_dir / "negative-controls-summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["test_id", args.test_id])
        w.writerow(["timestamp_utc", datetime.utcnow().isoformat(timespec="seconds") + "Z"])
        w.writerow(["lensing_csv", str(args.lensing_csv)])
        w.writerow(["rotation_csv", str(args.rotation_csv)])
        w.writerow(["n_runs_per_mode", str(max(1, args.n_runs))])
        w.writerow(["tau_fit_positive", fmt(tau)])
        w.writerow(["k_memory_fit_positive", fmt(k_mem)])
        w.writerow(["offset_score_positive", fmt(offset_pos)])
        w.writerow(["delta_chi2_lens_positive", fmt(d_lens_pos)])
        w.writerow(["delta_chi2_rot_positive", fmt(d_rot_pos)])
        w.writerow(["delta_chi2_total_positive", fmt(d_total_pos)])
        w.writerow(["delta_aic_total_positive", fmt(d_aic_pos)])
        w.writerow(["delta_chi2_lens_ctrl_median", fmt(median([r.delta_chi2_lens for r in lens_ctrl]))])
        w.writerow(["delta_chi2_rot_ctrl_median", fmt(median([r.delta_chi2_rot for r in rot_ctrl]))])
        w.writerow(["lensing_improvement_ratio_ctrl_vs_pos", fmt(lens_ratio)])
        w.writerow(["rotation_improvement_ratio_ctrl_vs_pos", fmt(rot_ratio)])
        w.writerow(["rule_lensing_control", str(lens_gate)])
        w.writerow(["rule_rotation_control", str(rot_gate)])
        w.writerow(["negative_control_pass", str(neg_control_pass)])
        w.writerow(["parse_warnings_count", str(len(lw) + len(rw))])

    runs_path = out_dir / "negative-controls-runs.csv"
    with runs_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "seed", "delta_chi2_lens", "delta_chi2_rot", "delta_chi2_total", "delta_aic_total"])
        for r in runs:
            w.writerow([r.mode, r.seed, fmt(r.delta_chi2_lens), fmt(r.delta_chi2_rot), fmt(r.delta_chi2_total), fmt(r.delta_aic_total)])

    md_path = out_dir / "negative-controls.md"
    md_lines = [
        f"# Negative Controls - {args.test_id}",
        "",
        f"- Lensing CSV: `{args.lensing_csv}`",
        f"- Rotation CSV: `{args.rotation_csv}`",
        f"- Runs per control mode: `{max(1, args.n_runs)}`",
        "",
        "## Positive Run (Reference)",
        "",
        f"- delta_chi2_lens: `{fmt(d_lens_pos)}`",
        f"- delta_chi2_rot: `{fmt(d_rot_pos)}`",
        f"- delta_chi2_total: `{fmt(d_total_pos)}`",
        f"- delta_aic_total: `{fmt(d_aic_pos)}`",
        f"- offset_score: `{fmt(offset_pos)}`",
        "",
        "## Control Gates",
        "",
        f"- Lensing permutation ratio (median control / positive): `{fmt(lens_ratio)}` (threshold `<= 0.20`) -> `{str(lens_gate).lower()}`",
        f"- Rotation permutation ratio (median control / positive): `{fmt(rot_ratio)}` (threshold `<= 0.20`) -> `{str(rot_gate).lower()}`",
        "",
        f"- Negative-control overall: `{str(neg_control_pass).lower()}`",
        "",
        "Interpretation:",
        "- If control ratios stay low, observed improvements are tied to structure in original pairings.",
        "- If ratios are high, the signal may leak through model flexibility or data construction artifacts.",
        "",
    ]
    if lw or rw:
        md_lines.append("Parse warnings:")
        for msg in lw + rw:
            md_lines.append(f"- {msg}")
        md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Negative controls completed. overall={neg_control_pass}")
    print(f"Summary: {summary_path}")
    print(f"Runs: {runs_path}")
    print(f"Report: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
