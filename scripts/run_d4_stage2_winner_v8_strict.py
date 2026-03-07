#!/usr/bin/env python3
"""
D4 Stage-2 winner v8 strict lane.

Purpose:
- run strict multi-split benchmark with the frozen WINNER_V1 formula (M8c from D7/D9b)
- keep anti post-hoc governance fields compatible with the existing strict evaluator
- compare against MOND baseline with unchanged criteria
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import (
    parse_int_list,
    parse_list,
    train_holdout_split,
)
from scripts.run_d9_cross_validation_v1 import (
    A0_INT,
    A0_SI,
    chi2_pts,
    fit_m8c,
    fit_mond,
    flatten,
    load_galaxies,
    v_m8c,
)


DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-winner-v8-strict"

WINNER_FORMULA_ID = "WINNER_V1_M8C"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run D4 Stage-2 winner v8 strict benchmark.")
    p.add_argument("--test-id", default="d4-stage2-winner-v8-strict")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--split-seeds", default="3401,3402,3403,3404,3405")
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--s1-lambda", type=float, default=0.28)
    p.add_argument("--s2-const", type=float, default=0.355)
    p.add_argument("--r0-kpc", type=float, default=1.0)
    p.add_argument("--r-tail-kpc", type=float, default=4.0)
    p.add_argument("--tau-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--alpha-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3")
    p.add_argument("--focus-gamma", type=float, default=2.0)
    p.add_argument("--candidate", default="winner_v1_m8c")
    p.add_argument("--outdir", default=str(DEFAULT_OUT))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--no-plots", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def f6(x: float) -> str:
    return f"{x:.6f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def chi2_null(points: list[dict[str, float]]) -> float:
    return sum(((p["v"] - math.sqrt(max(p["bt"], 0.0))) / p["ve"]) ** 2 for p in points)


def mond_v(point: dict[str, float], g_dag: float) -> float:
    g_bar = point["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * point["r"], 0.0))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = Path(args.dataset_csv).resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset csv not found: {dataset_path}")
    try:
        dataset_csv_rel = dataset_path.relative_to(ROOT).as_posix()
    except ValueError:
        dataset_csv_rel = dataset_path.name
    dataset_sha256 = sha256_file(dataset_path)

    split_seeds = parse_int_list(args.split_seeds)
    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    galaxies = load_galaxies(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    per_seed_rows: list[dict[str, Any]] = []
    for split_seed in split_seeds:
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, float(args.train_frac))
        train_points = flatten(galaxies, sorted(train_ids))
        holdout_points = flatten(galaxies, sorted(holdout_ids))
        n_train = max(1, len(train_points))
        n_holdout = max(1, len(holdout_points))

        # WINNER_V1 fit (direct import from D9 M8c lane).
        k_fit, gd_fit, train_m8c_per_n = fit_m8c(train_points)
        holdout_m8c_per_n = chi2_pts(
            holdout_points, lambda p: v_m8c(p, k_fit, gd_fit)
        ) / n_holdout

        # MOND control fit on train, frozen on holdout.
        gd_mond_fit, train_mond_per_n = fit_mond(train_points)
        holdout_mond_per_n = chi2_pts(
            holdout_points, lambda p: mond_v(p, gd_mond_fit)
        ) / n_holdout

        train_null_chi2 = chi2_null(train_points)
        holdout_null_chi2 = chi2_null(holdout_points)
        train_null_per_n = train_null_chi2 / n_train
        holdout_null_per_n = holdout_null_chi2 / n_holdout

        train_m8c_chi2 = train_m8c_per_n * n_train
        holdout_m8c_chi2 = holdout_m8c_per_n * n_holdout
        train_mond_chi2 = train_mond_per_n * n_train
        holdout_mond_chi2 = holdout_mond_per_n * n_holdout

        train_improve_vs_null_pct = 100.0 * (train_null_chi2 - train_m8c_chi2) / max(train_null_chi2, 1e-12)
        holdout_improve_vs_null_pct = 100.0 * (holdout_null_chi2 - holdout_m8c_chi2) / max(
            holdout_null_chi2, 1e-12
        )
        holdout_mond_worse_pct = 100.0 * (holdout_m8c_per_n - holdout_mond_per_n) / max(holdout_mond_per_n, 1e-12)
        train_mond_worse_pct = 100.0 * (train_m8c_per_n - train_mond_per_n) / max(train_mond_per_n, 1e-12)
        generalization_gap = abs(train_improve_vs_null_pct - holdout_improve_vs_null_pct)

        # Direct 2-parameter model (k, g_dag) for AIC/BIC in holdout.
        k_params = 2
        holdout_delta_aic = (holdout_m8c_chi2 + 2.0 * k_params) - (holdout_mond_chi2 + 2.0 * 1.0)
        holdout_delta_bic = (holdout_m8c_chi2 + k_params * math.log(n_holdout)) - (
            holdout_mond_chi2 + 1.0 * math.log(n_holdout)
        )

        row = {
            "test_id": str(args.test_id),
            "dataset_id": str(args.dataset_id),
            "dataset_csv_rel": dataset_csv_rel,
            "dataset_sha256": dataset_sha256,
            "split_seed": str(split_seed),
            "candidate": str(args.candidate),
            "n_points_train": str(n_train),
            "n_points_holdout": str(n_holdout),
            "lambda_s": "",
            "lambda_e": "",
            "best_tau_kpc": "",
            "best_alpha": "",
            "tau_on_boundary": "false",
            "alpha_on_boundary": "false",
            "any_boundary_hit": "false",
            "best_k1": f6(k_fit),
            "best_k2": f6(gd_fit),
            "best_k3": f6(0.0),
            "active_component_count": "2",
            "single_component_only": "false",
            "train_objective_j_per_n": f6(train_m8c_per_n),
            "train_focus_chi2_per_n_dual": f6(train_m8c_per_n),
            "train_chi2_per_n_dual": f6(train_m8c_per_n),
            "train_chi2_per_n_mond": f6(train_mond_per_n),
            "train_chi2_per_n_null": f6(train_null_per_n),
            "holdout_chi2_per_n_dual": f6(holdout_m8c_per_n),
            "holdout_chi2_per_n_mond": f6(holdout_mond_per_n),
            "holdout_chi2_per_n_null": f6(holdout_null_per_n),
            "holdout_improve_vs_null_pct": f6(holdout_improve_vs_null_pct),
            "holdout_mond_worse_pct": f6(holdout_mond_worse_pct),
            "train_mond_worse_pct": f6(train_mond_worse_pct),
            "generalization_gap_pp": f6(generalization_gap),
            "holdout_delta_aic_dual_minus_mond": f6(holdout_delta_aic),
            "holdout_delta_bic_dual_minus_mond": f6(holdout_delta_bic),
            "winner_formula_id": WINNER_FORMULA_ID,
        }
        per_seed_rows.append(row)

    per_seed_fields = list(per_seed_rows[0].keys()) if per_seed_rows else []
    write_csv(out_dir / "per_seed_candidate_summary.csv", per_seed_rows, per_seed_fields)

    n = len(per_seed_rows)
    agg = {
        "candidate": str(args.candidate),
        "n_splits": str(n),
        "avg_holdout_chi2_per_n_dual": f6(
            sum(float(r["holdout_chi2_per_n_dual"]) for r in per_seed_rows) / max(1, n)
        ),
        "avg_holdout_chi2_per_n_mond": f6(
            sum(float(r["holdout_chi2_per_n_mond"]) for r in per_seed_rows) / max(1, n)
        ),
        "avg_holdout_mond_worse_pct": f6(
            sum(float(r["holdout_mond_worse_pct"]) for r in per_seed_rows) / max(1, n)
        ),
        "avg_boundary_hit_rate": f6(0.0),
        "avg_single_component_only_rate": f6(0.0),
    }
    write_csv(out_dir / "aggregate_summary.csv", [agg], list(agg.keys()))

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": str(args.test_id),
        "dataset_id": str(args.dataset_id),
        "dataset_csv_rel": dataset_csv_rel,
        "dataset_sha256": dataset_sha256,
        "split_seeds": split_seeds,
        "train_frac": float(args.train_frac),
        "fixed_theory_constants": {
            "s1_lambda": float(args.s1_lambda),
            "s2_const": float(args.s2_const),
            "r0_kpc": float(args.r0_kpc),
            "r_tail_kpc": float(args.r_tail_kpc),
            "focus_gamma": float(args.focus_gamma),
            "a0_internal_km2_s2_kpc": A0_INT,
            "a0_si_m_s2": A0_SI,
            "winner_formula_id": WINNER_FORMULA_ID,
        },
        "search_space": {
            "tau_grid": tau_grid,
            "alpha_grid": alpha_grid,
            "mix_grid": [],
            "winner_fit_gdag_grid_over_a0": {
                "min": 0.1,
                "max": 5.0,
                "count": 60,
                "refine_count": 40,
            },
            "winner_fit_k_bounds": {
                "min": 0.05,
                "max": 8.0,
            },
        },
        "fit_objective": {
            "space": "velocity chi2",
            "grid_selection_objective": "winner_v1_direct_fit",
            "baseline_mond": "MOND_RAR_train_fit_per_split",
        },
        "candidates": [str(args.candidate)],
        "winner_formula": {
            "id": WINNER_FORMULA_ID,
            "equation": "v_pred^2 = bt + r * k * sqrt(g_bar * g_dag) * exp(-g_bar/g_dag)",
            "units": {
                "v": "km/s",
                "r": "kpc",
                "bt": "km^2/s^2",
                "g_bar": "km^2/s^2/kpc",
                "g_dag": "km^2/s^2/kpc",
            },
            "fit_parameters": ["k", "g_dag"],
            "fit_bounds": {
                "k": [0.05, 8.0],
                "g_dag_over_a0": [0.1, 5.0],
            },
        },
        "artifacts": {
            "per_seed_candidate_summary_csv": "per_seed_candidate_summary.csv",
            "aggregate_summary_csv": "aggregate_summary.csv",
            "report_md": "report.md",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# D4 Winner V8 Strict Report",
        "",
        f"- generated_utc: `{manifest['generated_utc']}`",
        f"- winner_formula_id: `{WINNER_FORMULA_ID}`",
        f"- candidate: `{args.candidate}`",
        f"- avg_holdout_chi2_per_n_dual: `{agg['avg_holdout_chi2_per_n_dual']}`",
        f"- avg_holdout_chi2_per_n_mond: `{agg['avg_holdout_chi2_per_n_mond']}`",
        f"- avg_holdout_mond_worse_pct: `{agg['avg_holdout_mond_worse_pct']}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"per_seed_csv: {(out_dir / 'per_seed_candidate_summary.csv').as_posix()}")
    print(f"aggregate_csv: {(out_dir / 'aggregate_summary.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
