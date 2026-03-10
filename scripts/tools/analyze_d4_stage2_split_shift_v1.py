#!/usr/bin/env python3
"""
D4 Stage-2 split-shift diagnostics v1.

Quantifies train-vs-holdout regime shift for each split seed using only
dataset geometry/acceleration features (no formula or threshold changes).
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import parse_int_list, train_holdout_split
from scripts.run_d9_cross_validation_v1 import A0_INT, flatten, load_galaxies


DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-split-shift-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze D4 train/holdout split shift across seeds.")
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--split-seeds", default="3401,3402,3403,3404,3405")
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--r-tail-kpc", type=float, default=4.0)
    p.add_argument(
        "--eval-csv",
        default=str(
            ROOT
            / "05_validation"
            / "evidence"
            / "artifacts"
            / "d4-stage2-winner-v10-strict"
            / "evaluation-v1"
            / "per_seed_evaluation.csv"
        ),
    )
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pct(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    q = max(0.0, min(1.0, q))
    i = int(round(q * (len(sorted_vals) - 1)))
    return sorted_vals[i]


def feature_summary(points: list[dict[str, float]], r_tail_kpc: float) -> dict[str, float]:
    if not points:
        return {
            "n_points": 0.0,
            "mean_log10_gbar": 0.0,
            "p10_log10_gbar": 0.0,
            "p50_log10_gbar": 0.0,
            "p90_log10_gbar": 0.0,
            "mean_r": 0.0,
            "p90_r": 0.0,
            "low_accel_outer_frac": 0.0,
        }
    log_g = sorted(math.log10(max(p["g_bar"], 1e-30)) for p in points)
    rs = sorted(p["r"] for p in points)
    low_outer = 0
    for p in points:
        g_bar = p["g_bar"]
        outer = p["r"] / max(p["r"] + r_tail_kpc, 1e-12)
        if g_bar < A0_INT and outer >= 0.60:
            low_outer += 1
    n = float(len(points))
    return {
        "n_points": n,
        "mean_log10_gbar": sum(log_g) / n,
        "p10_log10_gbar": pct(log_g, 0.10),
        "p50_log10_gbar": pct(log_g, 0.50),
        "p90_log10_gbar": pct(log_g, 0.90),
        "mean_r": sum(rs) / n,
        "p90_r": pct(rs, 0.90),
        "low_accel_outer_frac": low_outer / n,
    }


def get_eval_by_seed(eval_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for r in eval_rows:
        out[str(r.get("split_seed", ""))] = r
    return out


def f6(x: float) -> str:
    return f"{x:.6f}"


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = Path(args.dataset_csv).resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset csv not found: {dataset_path}")
    eval_path = Path(args.eval_csv).resolve()
    eval_rows = read_csv(eval_path) if eval_path.exists() else []
    eval_by_seed = get_eval_by_seed(eval_rows)

    galaxies = load_galaxies(dataset_path)
    galaxy_ids = sorted(galaxies.keys())
    seeds = parse_int_list(args.split_seeds)

    rows: list[dict[str, Any]] = []
    for seed in seeds:
        train_ids, hold_ids = train_holdout_split(galaxy_ids, seed, float(args.train_frac))
        train_pts = flatten(galaxies, sorted(train_ids))
        hold_pts = flatten(galaxies, sorted(hold_ids))

        tr = feature_summary(train_pts, float(args.r_tail_kpc))
        ho = feature_summary(hold_pts, float(args.r_tail_kpc))

        d_low_outer = abs(tr["low_accel_outer_frac"] - ho["low_accel_outer_frac"])
        d_mean_logg = abs(tr["mean_log10_gbar"] - ho["mean_log10_gbar"])
        d_p90_r = abs(tr["p90_r"] - ho["p90_r"])
        shift_score = d_low_outer + d_mean_logg + 0.05 * d_p90_r

        ev = eval_by_seed.get(str(seed), {})
        rows.append(
            {
                "split_seed": str(seed),
                "n_train_galaxies": str(len(train_ids)),
                "n_holdout_galaxies": str(len(hold_ids)),
                "n_train_points": str(len(train_pts)),
                "n_holdout_points": str(len(hold_pts)),
                "train_low_accel_outer_frac": f6(tr["low_accel_outer_frac"]),
                "holdout_low_accel_outer_frac": f6(ho["low_accel_outer_frac"]),
                "delta_low_accel_outer_frac": f6(d_low_outer),
                "train_mean_log10_gbar": f6(tr["mean_log10_gbar"]),
                "holdout_mean_log10_gbar": f6(ho["mean_log10_gbar"]),
                "delta_mean_log10_gbar": f6(d_mean_logg),
                "train_p90_r": f6(tr["p90_r"]),
                "holdout_p90_r": f6(ho["p90_r"]),
                "delta_p90_r": f6(d_p90_r),
                "split_shift_score": f6(shift_score),
                "v10_seed_decision": str(ev.get("seed_decision", "")),
                "v10_generalization_gap_pp": str(ev.get("generalization_gap_pp", "")),
                "v10_holdout_mond_worse_pct": str(ev.get("holdout_mond_worse_pct", "")),
            }
        )

    rows_sorted = sorted(rows, key=lambda r: float(r["split_shift_score"]), reverse=True)
    for rank, r in enumerate(rows_sorted, start=1):
        r["shift_rank"] = str(rank)

    def pearson(xs: list[float], ys: list[float]) -> float:
        n = min(len(xs), len(ys))
        if n < 2:
            return 0.0
        mx = sum(xs) / n
        my = sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        if sxx <= 1e-18 or syy <= 1e-18:
            return 0.0
        sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        return sxy / math.sqrt(sxx * syy)

    xs: list[float] = []
    ys: list[float] = []
    for r in rows_sorted:
        gap_s = str(r.get("v10_generalization_gap_pp", "")).strip()
        if not gap_s:
            continue
        xs.append(float(r["split_shift_score"]))
        ys.append(float(gap_s))
    corr_shift_vs_gap = pearson(xs, ys) if xs and ys else 0.0
    seed3403_rank = next((r["shift_rank"] for r in rows_sorted if r["split_seed"] == "3403"), "")

    fields = [
        "split_seed",
        "shift_rank",
        "n_train_galaxies",
        "n_holdout_galaxies",
        "n_train_points",
        "n_holdout_points",
        "train_low_accel_outer_frac",
        "holdout_low_accel_outer_frac",
        "delta_low_accel_outer_frac",
        "train_mean_log10_gbar",
        "holdout_mean_log10_gbar",
        "delta_mean_log10_gbar",
        "train_p90_r",
        "holdout_p90_r",
        "delta_p90_r",
        "split_shift_score",
        "v10_seed_decision",
        "v10_generalization_gap_pp",
        "v10_holdout_mond_worse_pct",
    ]
    write_csv(out_dir / "per_seed_shift.csv", rows_sorted, fields)

    top = rows_sorted[0] if rows_sorted else {}
    report = [
        "# D4 Split Shift Diagnostics v1",
        "",
        "Forensics-only train/holdout shift audit over fixed split seeds.",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- dataset_id: `{args.dataset_id}`",
        f"- split_seeds: `{','.join(str(x) for x in seeds)}`",
        f"- top shift seed: `{top.get('split_seed', '')}` (score={top.get('split_shift_score', '')})",
        f"- seed 3403 shift rank: `{seed3403_rank}`",
        f"- corr(split_shift_score, v10_generalization_gap_pp): `{f6(corr_shift_vs_gap)}`",
        "",
        "## Signal",
        "- `split_shift_score = |delta_low_accel_outer_frac| + |delta_mean_log10_gbar| + 0.05*|delta_p90_r|`",
        "- Higher score indicates stronger distribution mismatch between train and holdout.",
        "- If correlation vs gap is weak, global split-shift is not sufficient to explain HOLD behavior.",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "analysis_id": "d4-stage2-split-shift-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": args.dataset_id,
        "n_seeds": len(rows_sorted),
        "top_shift_seed": str(top.get("split_seed", "")),
        "top_shift_score": str(top.get("split_shift_score", "")),
        "seed3403_shift_rank": seed3403_rank,
        "corr_shift_score_vs_v10_gap": f6(corr_shift_vs_gap),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[ok] wrote split-shift package: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
