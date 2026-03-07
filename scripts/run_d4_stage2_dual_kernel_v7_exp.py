#!/usr/bin/env python3
"""
D4 Stage-2 v7 exploratory lane (no promotion).

Explores lambda_s/lambda_e regularization on fixed v7 formula and locked splits.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import (
    chi2_mond,
    fit_mond,
    parse_int_list,
    parse_list,
    read_data,
    train_holdout_split,
)
from scripts.tools._d4_v7_regularized import (
    design_columns_v7,
    edge_flags,
    evaluate_candidate_point,
    f6,
    make_rows_with_gid,
)

DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-v7-exp-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run D4 v7 exploratory regularization sweep.")
    p.add_argument("--test-id", default="d4-stage2-v7-exp-v1")
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
    p.add_argument("--lambda-s-grid", default="0,0.1,0.3,1.0")
    p.add_argument("--lambda-e-grid", default="0,0.1,0.3")
    p.add_argument("--focus-gamma", type=float, default=2.0)
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


def count_active(coeffs: list[float], eps: float) -> int:
    return sum(1 for x in coeffs if float(x) > eps)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = Path(args.dataset_csv).resolve()

    split_seeds = parse_int_list(args.split_seeds)
    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    lambda_s_grid = parse_list(args.lambda_s_grid)
    lambda_e_grid = parse_list(args.lambda_e_grid)

    galaxies = read_data(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    per_seed_rows: list[dict[str, Any]] = []
    for split_seed in split_seeds:
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, float(args.train_frac))
        train_points = [p for gid in sorted(train_ids) for p in galaxies[gid]]
        holdout_points = [p for gid in sorted(holdout_ids) for p in galaxies[gid]]
        g_dag, _ = fit_mond(train_points)
        holdout_mond_per_n = chi2_mond(holdout_points, g_dag) / max(1, len(holdout_points))

        # Cache data for each (tau, alpha) once per seed.
        cache: dict[tuple[float, float], dict[str, Any]] = {}
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
                cache[(tau, alpha)] = {
                    "train_rows": train_rows,
                    "holdout_rows": holdout_rows,
                    "train_cols": train_cols,
                    "holdout_cols": holdout_cols,
                    "tau_edge": tau_edge,
                    "alpha_edge": alpha_edge,
                }

        for lambda_s in lambda_s_grid:
            for lambda_e in lambda_e_grid:
                best_key = None
                best_payload: dict[str, Any] | None = None
                best_obj = float("inf")
                for tau in tau_grid:
                    for alpha in alpha_grid:
                        c = cache[(tau, alpha)]
                        payload = evaluate_candidate_point(
                            train_rows=c["train_rows"],
                            holdout_rows=c["holdout_rows"],
                            train_cols=c["train_cols"],
                            holdout_cols=c["holdout_cols"],
                            focus_gamma=float(args.focus_gamma),
                            r_tail_kpc=float(args.r_tail_kpc),
                            lambda_s=float(lambda_s),
                            lambda_e=float(lambda_e),
                            tau_on_edge=bool(c["tau_edge"]),
                            alpha_on_edge=bool(c["alpha_edge"]),
                            holdout_mond_per_n=holdout_mond_per_n,
                            n_train_points=len(train_points),
                            n_holdout_points=len(holdout_points),
                        )
                        if float(payload["train_objective_j_per_n"]) < best_obj:
                            best_obj = float(payload["train_objective_j_per_n"])
                            best_key = (tau, alpha, bool(c["tau_edge"]), bool(c["alpha_edge"]))
                            best_payload = payload

                assert best_key is not None and best_payload is not None
                coeffs = list(best_payload["coeffs"])
                active_count = count_active(coeffs, float(args.active_eps))
                row = {
                    "split_seed": str(split_seed),
                    "lambda_s": f6(lambda_s),
                    "lambda_e": f6(lambda_e),
                    "best_tau_kpc": f6(best_key[0]),
                    "best_alpha": f6(best_key[1]),
                    "tau_on_boundary": str(best_key[2]).lower(),
                    "alpha_on_boundary": str(best_key[3]).lower(),
                    "any_boundary_hit": str(best_key[2] or best_key[3]).lower(),
                    "best_k1": f6(coeffs[0] if len(coeffs) > 0 else 0.0),
                    "best_k2": f6(coeffs[1] if len(coeffs) > 1 else 0.0),
                    "active_component_count": str(active_count),
                    "single_component_only": str(active_count <= 1).lower(),
                    "train_objective_j_per_n": f6(float(best_payload["train_objective_j_per_n"])),
                    "train_focus_chi2_per_n_dual": f6(float(best_payload["train_focus_chi2_per_n_dual"])),
                    "train_chi2_per_n_dual": f6(float(best_payload["train_chi2_per_n_dual"])),
                    "holdout_chi2_per_n_dual": f6(float(best_payload["holdout_chi2_per_n_dual"])),
                    "holdout_chi2_per_n_mond": f6(holdout_mond_per_n),
                    "holdout_mond_worse_pct": f6(float(best_payload["holdout_mond_worse_pct"])),
                }
                per_seed_rows.append(row)

    per_seed_fields = [
        "split_seed",
        "lambda_s",
        "lambda_e",
        "best_tau_kpc",
        "best_alpha",
        "tau_on_boundary",
        "alpha_on_boundary",
        "any_boundary_hit",
        "best_k1",
        "best_k2",
        "active_component_count",
        "single_component_only",
        "train_objective_j_per_n",
        "train_focus_chi2_per_n_dual",
        "train_chi2_per_n_dual",
        "holdout_chi2_per_n_dual",
        "holdout_chi2_per_n_mond",
        "holdout_mond_worse_pct",
    ]
    write_csv(out_dir / "per_seed_lambda_summary.csv", per_seed_rows, per_seed_fields)

    # Aggregate by (lambda_s, lambda_e)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in per_seed_rows:
        grouped.setdefault((str(r["lambda_s"]), str(r["lambda_e"])), []).append(r)

    agg_rows: list[dict[str, Any]] = []
    for key in sorted(grouped.keys()):
        rows = grouped[key]
        n = len(rows)

        def avg(field: str) -> float:
            return sum(float(x[field]) for x in rows) / max(n, 1)

        b_hits = sum(1 for x in rows if x["any_boundary_hit"] == "true")
        s_lock = sum(1 for x in rows if x["single_component_only"] == "true")
        agg_rows.append(
            {
                "lambda_s": key[0],
                "lambda_e": key[1],
                "n_splits": str(n),
                "avg_holdout_mond_worse_pct": f6(avg("holdout_mond_worse_pct")),
                "avg_holdout_chi2_per_n_dual": f6(avg("holdout_chi2_per_n_dual")),
                "avg_holdout_chi2_per_n_mond": f6(avg("holdout_chi2_per_n_mond")),
                "avg_train_objective_j_per_n": f6(avg("train_objective_j_per_n")),
                "avg_boundary_hit_rate": f6(b_hits / max(n, 1)),
                "avg_single_component_only_rate": f6(s_lock / max(n, 1)),
            }
        )
    agg_fields = [
        "lambda_s",
        "lambda_e",
        "n_splits",
        "avg_holdout_mond_worse_pct",
        "avg_holdout_chi2_per_n_dual",
        "avg_holdout_chi2_per_n_mond",
        "avg_train_objective_j_per_n",
        "avg_boundary_hit_rate",
        "avg_single_component_only_rate",
    ]
    write_csv(out_dir / "aggregate_lambda_summary.csv", agg_rows, agg_fields)

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": str(args.test_id),
        "dataset_id": str(args.dataset_id),
        "dataset_csv": str(dataset_path),
        "split_seeds": split_seeds,
        "train_frac": float(args.train_frac),
        "fixed_theory_constants": {
            "s1_lambda": float(args.s1_lambda),
            "s2_const": float(args.s2_const),
            "r0_kpc": float(args.r0_kpc),
            "r_tail_kpc": float(args.r_tail_kpc),
            "focus_gamma": float(args.focus_gamma),
        },
        "search_space": {
            "tau_grid": tau_grid,
            "alpha_grid": alpha_grid,
            "lambda_s_grid": lambda_s_grid,
            "lambda_e_grid": lambda_e_grid,
        },
        "formula": "v_pred^2 = bt + k1*H1 + k2*Outer, k1,k2>=0",
        "artifacts": {
            "per_seed_lambda_summary_csv": "per_seed_lambda_summary.csv",
            "aggregate_lambda_summary_csv": "aggregate_lambda_summary.csv",
            "report_md": "report.md",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# D4 v7 Exploratory Report",
        "",
        "- exploratory-only: no promotion decision",
        f"- generated_utc: `{manifest['generated_utc']}`",
        "",
        "## Aggregate (lambda_s, lambda_e)",
        "",
    ]
    for row in agg_rows:
        lines.append(
            f"- `(lambda_s={row['lambda_s']}, lambda_e={row['lambda_e']})`: "
            f"holdout_mond_worse_pct={row['avg_holdout_mond_worse_pct']}, "
            f"boundary_hit_rate={row['avg_boundary_hit_rate']}, "
            f"single_component_rate={row['avg_single_component_only_rate']}"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"per_seed_csv: {(out_dir / 'per_seed_lambda_summary.csv').as_posix()}")
    print(f"aggregate_csv: {(out_dir / 'aggregate_lambda_summary.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
