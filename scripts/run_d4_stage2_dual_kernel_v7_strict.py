#!/usr/bin/env python3
"""
D4 Stage-2 v7 strict lane.

Uses one fixed lambda_s/lambda_e selected from v7-exp and runs strict multi-split evaluation package.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import (
    chi2_mond,
    chi2_null,
    fit_mond,
    parse_int_list,
    parse_list,
    read_data,
    train_holdout_split,
)
from scripts.tools._d4_v7_regularized import (
    count_active,
    design_columns_v7,
    edge_flags,
    evaluate_candidate_point,
    f6,
    make_rows_with_gid,
)

DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_SELECTED = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-v7-exp-v1" / "selected_config.json"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-dual-kernel-v7-strict"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run D4 v7 strict lane with fixed regularization lambdas.")
    p.add_argument("--test-id", default="d4-stage2-dual-kernel-v7-strict")
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
    p.add_argument("--selected-config-json", default=str(DEFAULT_SELECTED))
    p.add_argument("--lambda-s", type=float, default=float("nan"))
    p.add_argument("--lambda-e", type=float, default=float("nan"))
    p.add_argument("--candidate", default="outer_dual_reg_v7")
    p.add_argument("--active-eps", type=float, default=1e-9)
    p.add_argument("--outdir", default=str(DEFAULT_OUT))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--no-plots", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


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

    if math.isnan(float(args.lambda_s)) or math.isnan(float(args.lambda_e)):
        selected_path = Path(args.selected_config_json).resolve()
        if not selected_path.exists():
            raise FileNotFoundError(f"selected config json not found: {selected_path}")
        selected = json.loads(selected_path.read_text(encoding="utf-8"))
        lambda_s = float(selected["selected_lambda_s"])
        lambda_e = float(selected["selected_lambda_e"])
        selected_source = selected_path.as_posix()
    else:
        lambda_s = float(args.lambda_s)
        lambda_e = float(args.lambda_e)
        selected_source = ""

    split_seeds = parse_int_list(args.split_seeds)
    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    galaxies = read_data(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    per_seed_rows: list[dict[str, Any]] = []
    for split_seed in split_seeds:
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, float(args.train_frac))
        train_points = [p for gid in sorted(train_ids) for p in galaxies[gid]]
        holdout_points = [p for gid in sorted(holdout_ids) for p in galaxies[gid]]
        g_dag, train_mond_chi2 = fit_mond(train_points)
        holdout_mond_chi2 = chi2_mond(holdout_points, g_dag)
        train_null_chi2 = chi2_null(train_points)
        holdout_null_chi2 = chi2_null(holdout_points)

        best_train_obj = float("inf")
        best_train_focus = float("inf")
        best_train_chi2 = float("inf")
        best_holdout_chi2 = float("inf")
        best_tau = tau_grid[0]
        best_alpha = alpha_grid[0]
        best_coeffs: list[float] = [0.0, 0.0]
        best_tau_edge = False
        best_alpha_edge = False

        for tau in tau_grid:
            for alpha in alpha_grid:
                train_rows = make_rows_with_gid(
                    galaxies=galaxies,
                    ids=train_ids,
                    tau=tau,
                    alpha=alpha,
                    s1_lambda=float(args.s1_lambda),
                    s2_const=float(args.s2_const),
                    r0_kpc=float(args.r0_kpc),
                )
                holdout_rows = make_rows_with_gid(
                    galaxies=galaxies,
                    ids=holdout_ids,
                    tau=tau,
                    alpha=alpha,
                    s1_lambda=float(args.s1_lambda),
                    s2_const=float(args.s2_const),
                    r0_kpc=float(args.r0_kpc),
                )
                train_cols = design_columns_v7(train_rows, float(args.r_tail_kpc))
                holdout_cols = design_columns_v7(holdout_rows, float(args.r_tail_kpc))
                tau_edge, alpha_edge = edge_flags(tau, alpha, tau_grid, alpha_grid)

                payload = evaluate_candidate_point(
                    train_rows=train_rows,
                    holdout_rows=holdout_rows,
                    train_cols=train_cols,
                    holdout_cols=holdout_cols,
                    focus_gamma=float(args.focus_gamma),
                    r_tail_kpc=float(args.r_tail_kpc),
                    lambda_s=lambda_s,
                    lambda_e=lambda_e,
                    tau_on_edge=tau_edge,
                    alpha_on_edge=alpha_edge,
                    holdout_mond_per_n=holdout_mond_chi2 / max(1, len(holdout_points)),
                    n_train_points=len(train_points),
                    n_holdout_points=len(holdout_points),
                )
                train_obj = float(payload["train_objective_j_per_n"])
                if train_obj < best_train_obj:
                    best_train_obj = train_obj
                    best_train_focus = float(payload["train_focus_chi2_per_n_dual"])
                    best_train_chi2 = float(payload["train_chi2_per_n_dual"])
                    best_holdout_chi2 = float(payload["holdout_chi2_per_n_dual"])
                    best_tau = tau
                    best_alpha = alpha
                    best_coeffs = list(payload["coeffs"])
                    best_tau_edge = tau_edge
                    best_alpha_edge = alpha_edge

        holdout_dual_per_n = best_holdout_chi2
        train_dual_per_n = best_train_chi2
        train_mond_per_n = train_mond_chi2 / max(1, len(train_points))
        holdout_mond_per_n = holdout_mond_chi2 / max(1, len(holdout_points))
        train_null_per_n = train_null_chi2 / max(1, len(train_points))
        holdout_null_per_n = holdout_null_chi2 / max(1, len(holdout_points))

        train_improve_vs_null_pct = 100.0 * (train_null_chi2 - train_dual_per_n * len(train_points)) / max(
            train_null_chi2, 1e-12
        )
        holdout_improve_vs_null_pct = 100.0 * (
            holdout_null_chi2 - holdout_dual_per_n * len(holdout_points)
        ) / max(holdout_null_chi2, 1e-12)
        holdout_mond_worse_pct = 100.0 * (holdout_dual_per_n - holdout_mond_per_n) / max(holdout_mond_per_n, 1e-12)
        train_mond_worse_pct = 100.0 * (train_dual_per_n - train_mond_per_n) / max(train_mond_per_n, 1e-12)
        generalization_gap = abs(train_improve_vs_null_pct - holdout_improve_vs_null_pct)

        # v7 strict: search over tau+alpha (2) and two fitted coefficients.
        k_params = 4
        holdout_delta_aic = (
            (holdout_dual_per_n * len(holdout_points) + 2 * k_params)
            - (holdout_mond_chi2 + 2 * 1)
        )
        holdout_delta_bic = (
            (holdout_dual_per_n * len(holdout_points) + k_params * math.log(max(1, len(holdout_points))))
            - (holdout_mond_chi2 + 1 * math.log(max(1, len(holdout_points))))
        )
        active_count = count_active(best_coeffs, float(args.active_eps))

        row = {
            "test_id": str(args.test_id),
            "dataset_id": str(args.dataset_id),
            "dataset_csv_rel": dataset_csv_rel,
            "dataset_sha256": dataset_sha256,
            "split_seed": str(split_seed),
            "candidate": str(args.candidate),
            "n_points_train": str(len(train_points)),
            "n_points_holdout": str(len(holdout_points)),
            "lambda_s": f6(lambda_s),
            "lambda_e": f6(lambda_e),
            "best_tau_kpc": f6(best_tau),
            "best_alpha": f6(best_alpha),
            "tau_on_boundary": str(best_tau_edge).lower(),
            "alpha_on_boundary": str(best_alpha_edge).lower(),
            "any_boundary_hit": str(best_tau_edge or best_alpha_edge).lower(),
            "best_k1": f6(best_coeffs[0] if len(best_coeffs) > 0 else 0.0),
            "best_k2": f6(best_coeffs[1] if len(best_coeffs) > 1 else 0.0),
            "best_k3": f6(0.0),
            "active_component_count": str(active_count),
            "single_component_only": str(active_count <= 1).lower(),
            "train_objective_j_per_n": f6(best_train_obj),
            "train_focus_chi2_per_n_dual": f6(best_train_focus),
            "train_chi2_per_n_dual": f6(train_dual_per_n),
            "train_chi2_per_n_mond": f6(train_mond_per_n),
            "train_chi2_per_n_null": f6(train_null_per_n),
            "holdout_chi2_per_n_dual": f6(holdout_dual_per_n),
            "holdout_chi2_per_n_mond": f6(holdout_mond_per_n),
            "holdout_chi2_per_n_null": f6(holdout_null_per_n),
            "holdout_improve_vs_null_pct": f6(holdout_improve_vs_null_pct),
            "holdout_mond_worse_pct": f6(holdout_mond_worse_pct),
            "train_mond_worse_pct": f6(train_mond_worse_pct),
            "generalization_gap_pp": f6(generalization_gap),
            "holdout_delta_aic_dual_minus_mond": f6(holdout_delta_aic),
            "holdout_delta_bic_dual_minus_mond": f6(holdout_delta_bic),
        }
        per_seed_rows.append(row)

    per_seed_fields = list(per_seed_rows[0].keys()) if per_seed_rows else []
    write_csv(out_dir / "per_seed_candidate_summary.csv", per_seed_rows, per_seed_fields)

    n = len(per_seed_rows)
    agg = {
        "candidate": str(args.candidate),
        "n_splits": str(n),
        "lambda_s": f6(lambda_s),
        "lambda_e": f6(lambda_e),
        "avg_holdout_chi2_per_n_dual": f6(sum(float(r["holdout_chi2_per_n_dual"]) for r in per_seed_rows) / max(1, n)),
        "avg_holdout_chi2_per_n_mond": f6(sum(float(r["holdout_chi2_per_n_mond"]) for r in per_seed_rows) / max(1, n)),
        "avg_holdout_mond_worse_pct": f6(sum(float(r["holdout_mond_worse_pct"]) for r in per_seed_rows) / max(1, n)),
        "avg_boundary_hit_rate": f6(
            sum(1 for r in per_seed_rows if r["any_boundary_hit"] == "true") / max(1, n)
        ),
        "avg_single_component_only_rate": f6(
            sum(1 for r in per_seed_rows if r["single_component_only"] == "true") / max(1, n)
        ),
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
            "lambda_s": lambda_s,
            "lambda_e": lambda_e,
        },
        "search_space": {
            "tau_grid": tau_grid,
            "alpha_grid": alpha_grid,
        },
        "fit_objective": {
            "space": "velocity chi2 + regularizers",
            "grid_selection_objective": "train_focus_plus_regularizers",
        },
        "candidate": str(args.candidate),
        "selected_config_source": selected_source,
        "artifacts": {
            "per_seed_candidate_summary_csv": "per_seed_candidate_summary.csv",
            "aggregate_summary_csv": "aggregate_summary.csv",
            "report_md": "report.md",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# D4 v7 Strict Report",
        "",
        f"- generated_utc: `{manifest['generated_utc']}`",
        f"- lambda_s: `{f6(lambda_s)}`",
        f"- lambda_e: `{f6(lambda_e)}`",
        f"- avg_holdout_mond_worse_pct: `{agg['avg_holdout_mond_worse_pct']}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"per_seed_csv: {(out_dir / 'per_seed_candidate_summary.csv').as_posix()}")
    print(f"aggregate_csv: {(out_dir / 'aggregate_summary.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
