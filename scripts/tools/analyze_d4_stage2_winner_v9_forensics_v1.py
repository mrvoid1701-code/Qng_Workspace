#!/usr/bin/env python3
"""Forensics for D4 winner lane on a target split seed (default: 3403)."""

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

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import train_holdout_split
from scripts.run_d9_cross_validation_v1 import A0_INT, fit_m8c, fit_mond, flatten, load_galaxies, v_m8c


DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v9-forensics-seed3403-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze D4 winner v9 forensics for one split seed.")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--seed", type=int, default=3403)
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def mond_v(point: dict[str, float], g_dag: float) -> float:
    g_bar = point["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * point["r"], 0.0))


def null_v(point: dict[str, float]) -> float:
    return math.sqrt(max(point["bt"], 0.0))


def accel_bin(point: dict[str, float]) -> str:
    chi = point["g_bar"] / max(A0_INT, 1e-30)
    if chi < 1.0:
        return "low_accel"
    if chi < 10.0:
        return "mid_accel"
    return "high_accel"


def f6(x: float) -> str:
    return f"{x:.6f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def summarize_points(rows: list[dict[str, Any]]) -> dict[str, float]:
    n = max(1, len(rows))
    c2_w = sum(float(r["chi2_winner"]) for r in rows)
    c2_m = sum(float(r["chi2_mond"]) for r in rows)
    c2_n = sum(float(r["chi2_null"]) for r in rows)
    return {
        "n_points": float(n),
        "chi2_per_n_winner": c2_w / n,
        "chi2_per_n_mond": c2_m / n,
        "chi2_per_n_null": c2_n / n,
        "winner_over_mond": (c2_w / n) / max(c2_m / n, 1e-12),
        "improve_vs_null_pct": 100.0 * ((c2_n / n) - (c2_w / n)) / max(c2_n / n, 1e-12),
    }


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = Path(args.dataset_csv).resolve()
    galaxies = load_galaxies(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    train_ids, holdout_ids = train_holdout_split(galaxy_ids, int(args.seed), float(args.train_frac))
    train_points = flatten(galaxies, sorted(train_ids))
    holdout_points = flatten(galaxies, sorted(holdout_ids))

    k_fit, gd_fit, train_w_per_n = fit_m8c(train_points)
    gd_mond_fit, train_m_per_n = fit_mond(train_points)
    holdout_w_per_n = sum(
        ((p["v"] - v_m8c(p, k_fit, gd_fit)) / p["ve"]) ** 2 for p in holdout_points
    ) / max(1, len(holdout_points))
    holdout_m_per_n = sum(
        ((p["v"] - mond_v(p, gd_mond_fit)) / p["ve"]) ** 2 for p in holdout_points
    ) / max(1, len(holdout_points))
    train_n_per_n = sum(((p["v"] - null_v(p)) / p["ve"]) ** 2 for p in train_points) / max(1, len(train_points))
    holdout_n_per_n = sum(((p["v"] - null_v(p)) / p["ve"]) ** 2 for p in holdout_points) / max(1, len(holdout_points))

    train_improve = 100.0 * (train_n_per_n - train_w_per_n) / max(train_n_per_n, 1e-12)
    holdout_improve = 100.0 * (holdout_n_per_n - holdout_w_per_n) / max(holdout_n_per_n, 1e-12)
    generalization_gap = abs(train_improve - holdout_improve)

    point_rows: list[dict[str, Any]] = []
    for split_name, ids in (("train", train_ids), ("holdout", holdout_ids)):
        for gid in sorted(ids):
            pts = galaxies[gid]
            n = max(1, len(pts))
            for i, p in enumerate(pts):
                q = (i + 0.5) / n
                if q <= 1.0 / 3.0:
                    rbin = "inner"
                elif q <= 2.0 / 3.0:
                    rbin = "mid"
                else:
                    rbin = "outer"
                v_w = v_m8c(p, k_fit, gd_fit)
                v_m = mond_v(p, gd_mond_fit)
                v_n = null_v(p)
                c2_w = ((p["v"] - v_w) / p["ve"]) ** 2
                c2_m = ((p["v"] - v_m) / p["ve"]) ** 2
                c2_n = ((p["v"] - v_n) / p["ve"]) ** 2
                point_rows.append(
                    {
                        "split": split_name,
                        "galaxy": gid,
                        "radius_kpc": p["r"],
                        "gbar_over_a0": p["g_bar"] / max(A0_INT, 1e-30),
                        "accel_bin": accel_bin(p),
                        "radial_bin": rbin,
                        "chi2_winner": c2_w,
                        "chi2_mond": c2_m,
                        "chi2_null": c2_n,
                    }
                )

    # Per-galaxy summaries.
    by_gal: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in point_rows:
        by_gal.setdefault((str(r["split"]), str(r["galaxy"])), []).append(r)
    gal_rows: list[dict[str, Any]] = []
    for (split_name, gid), rr in sorted(by_gal.items()):
        s = summarize_points(rr)
        gal_rows.append(
            {
                "split": split_name,
                "galaxy": gid,
                "n_points": str(int(s["n_points"])),
                "chi2_per_n_winner": f6(s["chi2_per_n_winner"]),
                "chi2_per_n_mond": f6(s["chi2_per_n_mond"]),
                "chi2_per_n_null": f6(s["chi2_per_n_null"]),
                "winner_over_mond": f6(s["winner_over_mond"]),
                "improve_vs_null_pct": f6(s["improve_vs_null_pct"]),
            }
        )
    write_csv(
        out_dir / "per_galaxy_split_metrics.csv",
        gal_rows,
        [
            "split",
            "galaxy",
            "n_points",
            "chi2_per_n_winner",
            "chi2_per_n_mond",
            "chi2_per_n_null",
            "winner_over_mond",
            "improve_vs_null_pct",
        ],
    )

    # Regime summaries.
    reg_rows: list[dict[str, Any]] = []
    for split_name in ("train", "holdout"):
        for ab in ("low_accel", "mid_accel", "high_accel"):
            rr = [r for r in point_rows if r["split"] == split_name and r["accel_bin"] == ab]
            if not rr:
                continue
            s = summarize_points(rr)
            reg_rows.append(
                {
                    "group": "accel",
                    "split": split_name,
                    "bin": ab,
                    "n_points": str(int(s["n_points"])),
                    "chi2_per_n_winner": f6(s["chi2_per_n_winner"]),
                    "chi2_per_n_mond": f6(s["chi2_per_n_mond"]),
                    "winner_over_mond": f6(s["winner_over_mond"]),
                    "improve_vs_null_pct": f6(s["improve_vs_null_pct"]),
                }
            )
        for rb in ("inner", "mid", "outer"):
            rr = [r for r in point_rows if r["split"] == split_name and r["radial_bin"] == rb]
            if not rr:
                continue
            s = summarize_points(rr)
            reg_rows.append(
                {
                    "group": "radial",
                    "split": split_name,
                    "bin": rb,
                    "n_points": str(int(s["n_points"])),
                    "chi2_per_n_winner": f6(s["chi2_per_n_winner"]),
                    "chi2_per_n_mond": f6(s["chi2_per_n_mond"]),
                    "winner_over_mond": f6(s["winner_over_mond"]),
                    "improve_vs_null_pct": f6(s["improve_vs_null_pct"]),
                }
            )
    write_csv(
        out_dir / "regime_summary.csv",
        reg_rows,
        [
            "group",
            "split",
            "bin",
            "n_points",
            "chi2_per_n_winner",
            "chi2_per_n_mond",
            "winner_over_mond",
            "improve_vs_null_pct",
        ],
    )

    holdout_worst = sorted(
        [r for r in gal_rows if r["split"] == "holdout"],
        key=lambda x: float(x["winner_over_mond"]),
        reverse=True,
    )[:10]
    write_csv(
        out_dir / "holdout_top_worst_galaxies.csv",
        holdout_worst,
        [
            "split",
            "galaxy",
            "n_points",
            "chi2_per_n_winner",
            "chi2_per_n_mond",
            "chi2_per_n_null",
            "winner_over_mond",
            "improve_vs_null_pct",
        ],
    )

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": str(args.dataset_id),
        "dataset_csv": dataset_path.as_posix(),
        "seed": int(args.seed),
        "train_frac": float(args.train_frac),
        "winner_formula_id": "WINNER_V1_M8C",
        "fit_params": {
            "k": k_fit,
            "g_dag_internal": gd_fit,
            "g_dag_mond_internal": gd_mond_fit,
        },
        "train": {
            "chi2_per_n_winner": train_w_per_n,
            "chi2_per_n_mond": train_m_per_n,
            "chi2_per_n_null": train_n_per_n,
            "improve_vs_null_pct": train_improve,
        },
        "holdout": {
            "chi2_per_n_winner": holdout_w_per_n,
            "chi2_per_n_mond": holdout_m_per_n,
            "chi2_per_n_null": holdout_n_per_n,
            "improve_vs_null_pct": holdout_improve,
            "mond_worse_pct": 100.0 * (holdout_w_per_n - holdout_m_per_n) / max(holdout_m_per_n, 1e-12),
        },
        "generalization_gap_pp": generalization_gap,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "# D4 Winner V9 Forensics (Seed-Focused)",
        "",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- dataset_id: `{summary['dataset_id']}`",
        f"- seed: `{summary['seed']}`",
        f"- winner_formula_id: `WINNER_V1_M8C`",
        f"- train chi2/N (winner, mond, null): `{f6(train_w_per_n)}`, `{f6(train_m_per_n)}`, `{f6(train_n_per_n)}`",
        f"- holdout chi2/N (winner, mond, null): `{f6(holdout_w_per_n)}`, `{f6(holdout_m_per_n)}`, `{f6(holdout_n_per_n)}`",
        f"- train improve vs null (%): `{f6(train_improve)}`",
        f"- holdout improve vs null (%): `{f6(holdout_improve)}`",
        f"- generalization_gap_pp: `{f6(generalization_gap)}`",
        "",
        "## Diagnostic Focus",
        "",
        "- inspect `regime_summary.csv` for train vs holdout differences by accel/radial bins",
        "- inspect `holdout_top_worst_galaxies.csv` for concentration of failure pressure",
        "- no thresholds/formulas changed; this run is forensics-only",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"summary_json: {(out_dir / 'summary.json').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
