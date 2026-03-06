#!/usr/bin/env python3
"""
D4 Stage-2 v6 forensics (exploratory, no promotion).

Outputs:
- objective 2D maps on (tau, alpha): train_focus_chi2 and holdout_chi2
- identifiability diagnostics: column correlation + condition number
- boundary-hit rates (tau/alpha at grid edges)
- active-component counts from v5 best-fit summaries
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

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import (  # noqa: E402
    A0_INTERNAL,
    chi2_candidate,
    chi2_focus_candidate,
    chi2_mond,
    design_columns,
    fit_mond,
    fit_nonneg_chi2_v,
    f6,
    make_rows_for_ids,
    parse_int_list,
    parse_list,
    read_data,
    safe_rate,
    train_holdout_split,
)

DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_PER_SEED = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v5-candidates"
    / "per_seed_candidate_summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-v6-forensics-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run D4 v6 exploratory forensics over v5 locked setup.")
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
    p.add_argument("--candidates", default="outer_lowaccel_single,outer_lowaccel_focus")
    p.add_argument("--per-seed-summary-csv", default=str(DEFAULT_PER_SEED))
    p.add_argument("--active-eps", type=float, default=1e-9)
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


def pearson_corr(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n == 0 or n != len(ys):
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-18 or vy <= 1e-18:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def cond_xtx_2col(col_a: list[float], col_b: list[float]) -> float:
    if len(col_a) != len(col_b) or not col_a:
        return 0.0
    s11 = sum(x * x for x in col_a)
    s22 = sum(y * y for y in col_b)
    s12 = sum(x * y for x, y in zip(col_a, col_b))
    tr = s11 + s22
    det = s11 * s22 - s12 * s12
    if det <= 0.0:
        return float("inf")
    disc = max(tr * tr - 4.0 * det, 0.0)
    lam_max = 0.5 * (tr + math.sqrt(disc))
    lam_min = 0.5 * (tr - math.sqrt(disc))
    if lam_min <= 1e-18:
        return float("inf")
    return lam_max / lam_min


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    xs = sorted(vals)
    idx = int(max(0, min(len(xs) - 1, math.floor(q * (len(xs) - 1)))))
    return xs[idx]


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = Path(args.dataset_csv).resolve()
    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset csv not found: {dataset_path}")
    per_seed_path = Path(args.per_seed_summary_csv).resolve()
    if not per_seed_path.exists():
        raise FileNotFoundError(f"per-seed summary csv not found: {per_seed_path}")

    split_seeds = parse_int_list(args.split_seeds)
    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    candidates = [x.strip() for x in str(args.candidates).split(",") if x.strip()]
    for c in candidates:
        if c not in {"outer_lowaccel_single", "outer_lowaccel_focus"}:
            raise ValueError(f"unsupported candidate: {c}")

    galaxies = read_data(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    objective_rows: list[dict[str, Any]] = []
    ident_rows: list[dict[str, Any]] = []
    for split_seed in split_seeds:
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, float(args.train_frac))
        train_points = [p for gid in sorted(train_ids) for p in galaxies[gid]]
        holdout_points = [p for gid in sorted(holdout_ids) for p in galaxies[gid]]
        g_dag, _ = fit_mond(train_points)
        holdout_mond_chi2 = chi2_mond(holdout_points, g_dag)
        holdout_mond_per_n = safe_rate(holdout_mond_chi2, len(holdout_points))

        for tau in tau_grid:
            for alpha in alpha_grid:
                train_rows = make_rows_for_ids(
                    galaxies=galaxies,
                    ids=train_ids,
                    tau=tau,
                    alpha=alpha,
                    s1_lambda=float(args.s1_lambda),
                    s2_const=float(args.s2_const),
                    r0_kpc=float(args.r0_kpc),
                )
                holdout_rows = make_rows_for_ids(
                    galaxies=galaxies,
                    ids=holdout_ids,
                    tau=tau,
                    alpha=alpha,
                    s1_lambda=float(args.s1_lambda),
                    s2_const=float(args.s2_const),
                    r0_kpc=float(args.r0_kpc),
                )

                # Identifiability features are measured on [H1, outer-lowaccel] basis.
                id_cols = design_columns(
                    train_rows,
                    "outer_lowaccel_focus",
                    float(args.r_tail_kpc),
                    A0_INTERNAL,
                )
                corr_h1_outer = pearson_corr(id_cols[0], id_cols[1])
                cond_xtx = cond_xtx_2col(id_cols[0], id_cols[1])
                ident_rows.append(
                    {
                        "split_seed": str(split_seed),
                        "tau_kpc": f6(tau),
                        "alpha": f6(alpha),
                        "corr_h1_outer": f6(corr_h1_outer),
                        "cond_xtx_h1_outer": f6(cond_xtx) if math.isfinite(cond_xtx) else "inf",
                    }
                )

                for candidate in candidates:
                    train_cols = design_columns(
                        train_rows,
                        candidate,
                        float(args.r_tail_kpc),
                        A0_INTERNAL,
                    )
                    holdout_cols = design_columns(
                        holdout_rows,
                        candidate,
                        float(args.r_tail_kpc),
                        A0_INTERNAL,
                    )
                    coeffs = fit_nonneg_chi2_v(
                        train_rows,
                        train_cols,
                        focus_gamma=float(args.focus_gamma),
                        r_tail_kpc=float(args.r_tail_kpc),
                        a0_internal=A0_INTERNAL,
                    )
                    train_focus_chi2 = chi2_focus_candidate(
                        train_rows,
                        coeffs,
                        train_cols,
                        focus_gamma=float(args.focus_gamma),
                        r_tail_kpc=float(args.r_tail_kpc),
                        a0_internal=A0_INTERNAL,
                    )
                    holdout_chi2 = chi2_candidate(holdout_rows, coeffs, holdout_cols)
                    holdout_dual_per_n = safe_rate(holdout_chi2, len(holdout_points))
                    holdout_mond_worse = 100.0 * (holdout_dual_per_n - holdout_mond_per_n) / max(holdout_mond_per_n, 1e-12)
                    objective_rows.append(
                        {
                            "split_seed": str(split_seed),
                            "candidate": candidate,
                            "tau_kpc": f6(tau),
                            "alpha": f6(alpha),
                            "k1": f6(coeffs[0] if len(coeffs) > 0 else 0.0),
                            "k2": f6(coeffs[1] if len(coeffs) > 1 else 0.0),
                            "k3": f6(coeffs[2] if len(coeffs) > 2 else 0.0),
                            "train_focus_chi2_per_n_dual": f6(safe_rate(train_focus_chi2, len(train_points))),
                            "holdout_chi2_per_n_dual": f6(holdout_dual_per_n),
                            "holdout_chi2_per_n_mond": f6(holdout_mond_per_n),
                            "holdout_mond_worse_pct": f6(holdout_mond_worse),
                        }
                    )

    objective_fields = [
        "split_seed",
        "candidate",
        "tau_kpc",
        "alpha",
        "k1",
        "k2",
        "k3",
        "train_focus_chi2_per_n_dual",
        "holdout_chi2_per_n_dual",
        "holdout_chi2_per_n_mond",
        "holdout_mond_worse_pct",
    ]
    write_csv(out_dir / "objective_surface.csv", objective_rows, objective_fields)

    ident_fields = ["split_seed", "tau_kpc", "alpha", "corr_h1_outer", "cond_xtx_h1_outer"]
    write_csv(out_dir / "identifiability_surface.csv", ident_rows, ident_fields)

    per_seed_rows = read_csv(per_seed_path)
    tau_min = min(tau_grid)
    tau_max = max(tau_grid)
    alpha_min = min(alpha_grid)
    alpha_max = max(alpha_grid)
    active_eps = float(args.active_eps)
    boundary_rows: list[dict[str, Any]] = []
    active_rows: list[dict[str, Any]] = []
    for r in per_seed_rows:
        tau = float(r["best_tau_kpc"])
        alpha = float(r["best_alpha"])
        k1 = float(r["best_k1"])
        k2 = float(r["best_k2"])
        k3 = float(r["best_k3"])
        tau_edge = abs(tau - tau_min) <= 1e-12 or abs(tau - tau_max) <= 1e-12
        alpha_edge = abs(alpha - alpha_min) <= 1e-12 or abs(alpha - alpha_max) <= 1e-12
        n_active = int(k1 > active_eps) + int(k2 > active_eps) + int(k3 > active_eps)
        boundary_rows.append(
            {
                "split_seed": str(r["split_seed"]),
                "candidate": str(r["candidate"]),
                "best_tau_kpc": f6(tau),
                "best_alpha": f6(alpha),
                "tau_on_boundary": str(tau_edge).lower(),
                "alpha_on_boundary": str(alpha_edge).lower(),
                "any_boundary_hit": str(tau_edge or alpha_edge).lower(),
            }
        )
        active_rows.append(
            {
                "split_seed": str(r["split_seed"]),
                "candidate": str(r["candidate"]),
                "best_k1": f6(k1),
                "best_k2": f6(k2),
                "best_k3": f6(k3),
                "active_component_count": str(n_active),
                "single_component_only": str(n_active <= 1).lower(),
            }
        )

    write_csv(
        out_dir / "boundary_hits.csv",
        boundary_rows,
        ["split_seed", "candidate", "best_tau_kpc", "best_alpha", "tau_on_boundary", "alpha_on_boundary", "any_boundary_hit"],
    )
    write_csv(
        out_dir / "active_components.csv",
        active_rows,
        ["split_seed", "candidate", "best_k1", "best_k2", "best_k3", "active_component_count", "single_component_only"],
    )

    # Summaries
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for r in boundary_rows:
        by_candidate.setdefault(str(r["candidate"]), []).append(r)
    boundary_summary_rows: list[dict[str, Any]] = []
    for candidate in sorted(by_candidate.keys()):
        rows = by_candidate[candidate]
        n = len(rows)
        tau_hits = sum(1 for x in rows if x["tau_on_boundary"] == "true")
        alpha_hits = sum(1 for x in rows if x["alpha_on_boundary"] == "true")
        any_hits = sum(1 for x in rows if x["any_boundary_hit"] == "true")
        boundary_summary_rows.append(
            {
                "candidate": candidate,
                "n_splits": str(n),
                "tau_boundary_hit_rate": f6(tau_hits / max(n, 1)),
                "alpha_boundary_hit_rate": f6(alpha_hits / max(n, 1)),
                "any_boundary_hit_rate": f6(any_hits / max(n, 1)),
            }
        )
    write_csv(
        out_dir / "boundary_hit_summary.csv",
        boundary_summary_rows,
        ["candidate", "n_splits", "tau_boundary_hit_rate", "alpha_boundary_hit_rate", "any_boundary_hit_rate"],
    )

    corr_vals = [abs(float(r["corr_h1_outer"])) for r in ident_rows]
    cond_vals = [float(r["cond_xtx_h1_outer"]) for r in ident_rows if r["cond_xtx_h1_outer"] != "inf"]
    inf_cond = sum(1 for r in ident_rows if r["cond_xtx_h1_outer"] == "inf")
    high_corr_rate = sum(1 for x in corr_vals if x >= 0.98) / max(1, len(corr_vals))
    med_abs_corr = percentile(corr_vals, 0.50)
    p90_abs_corr = percentile(corr_vals, 0.90)
    med_cond = percentile(cond_vals, 0.50) if cond_vals else float("inf")
    p90_cond = percentile(cond_vals, 0.90) if cond_vals else float("inf")
    any_boundary_rate = (
        sum(1 for x in boundary_rows if x["any_boundary_hit"] == "true") / max(1, len(boundary_rows))
    )
    single_component_rate = (
        sum(1 for x in active_rows if x["single_component_only"] == "true") / max(1, len(active_rows))
    )

    collinearity_collapse = (
        high_corr_rate >= 0.50 and any_boundary_rate >= 0.50 and single_component_rate >= 0.80
    )
    boundary_pressure_collapse = (
        any_boundary_rate >= 0.90 and single_component_rate >= 0.90
    )
    if collinearity_collapse:
        decision = "IDENTIFIABILITY_COLLAPSE_LIKELY"
    elif boundary_pressure_collapse:
        decision = "BOUNDARY_PRESSURE_COLLAPSE_LIKELY"
    else:
        decision = "NO_STRONG_COLLAPSE_SIGNAL"

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
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
        "grids": {"tau_grid": tau_grid, "alpha_grid": alpha_grid},
        "candidates": candidates,
        "inputs": {"per_seed_summary_csv": str(per_seed_path)},
        "summary": {
            "high_abs_corr_rate_ge_0p98": high_corr_rate,
            "median_abs_corr": med_abs_corr,
            "p90_abs_corr": p90_abs_corr,
            "median_cond_xtx": med_cond,
            "p90_cond_xtx": p90_cond,
            "inf_cond_count": inf_cond,
            "any_boundary_hit_rate": any_boundary_rate,
            "single_component_only_rate": single_component_rate,
            "collinearity_collapse_flag": collinearity_collapse,
            "boundary_pressure_collapse_flag": boundary_pressure_collapse,
            "decision": decision,
        },
        "artifacts": {
            "objective_surface_csv": "objective_surface.csv",
            "identifiability_surface_csv": "identifiability_surface.csv",
            "boundary_hits_csv": "boundary_hits.csv",
            "boundary_hit_summary_csv": "boundary_hit_summary.csv",
            "active_components_csv": "active_components.csv",
            "report_md": "report.md",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# D4 v6 Forensics v1",
        "",
        "- exploratory only: no promotion, no threshold changes",
        f"- generated_utc: `{manifest['generated_utc']}`",
        f"- decision: `{decision}`",
        "",
        "## Core Signals",
        "",
        f"- high |corr(H1,outer)| rate (>=0.98): `{f6(high_corr_rate)}`",
        f"- median |corr(H1,outer)|: `{f6(med_abs_corr)}`",
        f"- p90 |corr(H1,outer)|: `{f6(p90_abs_corr)}`",
        f"- median cond(X^T X): `{f6(med_cond) if math.isfinite(med_cond) else 'inf'}`",
        f"- p90 cond(X^T X): `{f6(p90_cond) if math.isfinite(p90_cond) else 'inf'}`",
        f"- infinite-cond count: `{inf_cond}`",
        f"- boundary-hit rate (any): `{f6(any_boundary_rate)}`",
        f"- single-component-only rate: `{f6(single_component_rate)}`",
        "",
        "## Interpretation",
        "",
    ]
    if collinearity_collapse:
        lines.append(
            "- signal is consistent with identifiability collapse (high collinearity + boundary pressure + component sparsity)"
        )
    elif boundary_pressure_collapse:
        lines.append(
            "- signal is consistent with boundary-pressure collapse (grid-edge lock + single-component lock) even without extreme collinearity"
        )
    else:
        lines.append("- no strong collapse signature under current heuristic; inspect surfaces directly")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append("- `objective_surface.csv`")
    lines.append("- `identifiability_surface.csv`")
    lines.append("- `boundary_hits.csv`")
    lines.append("- `boundary_hit_summary.csv`")
    lines.append("- `active_components.csv`")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"objective_surface_csv: {(out_dir / 'objective_surface.csv').as_posix()}")
    print(f"identifiability_surface_csv: {(out_dir / 'identifiability_surface.csv').as_posix()}")
    print(f"boundary_hits_csv: {(out_dir / 'boundary_hits.csv').as_posix()}")
    print(f"active_components_csv: {(out_dir / 'active_components.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    print(f"decision: {decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
