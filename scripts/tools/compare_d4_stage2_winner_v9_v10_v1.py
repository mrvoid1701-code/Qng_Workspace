#!/usr/bin/env python3
"""Compare D4 winner v9 vs v10 strict outcomes per split seed."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_V9 = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v9-strict"
    / "evaluation-v1"
    / "per_seed_evaluation.csv"
)
DEFAULT_V10 = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v10-strict"
    / "evaluation-v1"
    / "per_seed_evaluation.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v10-strict"
    / "comparison-v9-v10-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare per-seed strict evaluation between D4 winner v9 and v10.")
    p.add_argument("--v9-csv", default=str(DEFAULT_V9))
    p.add_argument("--v10-csv", default=str(DEFAULT_V10))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def f6(x: float) -> str:
    return f"{x:.6f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    v9_path = Path(args.v9_csv).resolve()
    v10_path = Path(args.v10_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    v9_rows = read_csv(v9_path)
    v10_rows = read_csv(v10_path)
    v9_by_seed = {int(r["split_seed"]): r for r in v9_rows}
    v10_by_seed = {int(r["split_seed"]): r for r in v10_rows}
    seeds = sorted(set(v9_by_seed.keys()) & set(v10_by_seed.keys()))

    cmp_rows: list[dict[str, str]] = []
    for seed in seeds:
        a = v9_by_seed[seed]
        b = v10_by_seed[seed]
        gap_a = float(a["generalization_gap_pp"])
        gap_b = float(b["generalization_gap_pp"])
        mond_a = float(a["holdout_mond_worse_pct"])
        mond_b = float(b["holdout_mond_worse_pct"])
        c2_a = float(a["holdout_chi2_per_n_dual"])
        c2_b = float(b["holdout_chi2_per_n_dual"])
        cmp_rows.append(
            {
                "split_seed": str(seed),
                "v9_seed_decision": str(a["seed_decision"]),
                "v10_seed_decision": str(b["seed_decision"]),
                "v9_generalization_gap_pp": f6(gap_a),
                "v10_generalization_gap_pp": f6(gap_b),
                "delta_gap_pp_v10_minus_v9": f6(gap_b - gap_a),
                "v9_holdout_mond_worse_pct": f6(mond_a),
                "v10_holdout_mond_worse_pct": f6(mond_b),
                "delta_holdout_mond_worse_pct_v10_minus_v9": f6(mond_b - mond_a),
                "v9_holdout_chi2_per_n_dual": f6(c2_a),
                "v10_holdout_chi2_per_n_dual": f6(c2_b),
                "delta_holdout_chi2_per_n_dual_v10_minus_v9": f6(c2_b - c2_a),
            }
        )

    fields = list(cmp_rows[0].keys()) if cmp_rows else []
    write_csv(out_dir / "seed_comparison.csv", cmp_rows, fields)

    # Focus summary for seed 3403 and overall means.
    def mean_of(key: str) -> float:
        if not cmp_rows:
            return 0.0
        return sum(float(r[key]) for r in cmp_rows) / len(cmp_rows)

    s3403 = next((r for r in cmp_rows if r["split_seed"] == "3403"), None)
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "v9_csv": v9_path.as_posix(),
        "v10_csv": v10_path.as_posix(),
        "n_seeds_compared": len(cmp_rows),
        "mean_delta_gap_pp_v10_minus_v9": mean_of("delta_gap_pp_v10_minus_v9"),
        "mean_delta_holdout_mond_worse_pct_v10_minus_v9": mean_of("delta_holdout_mond_worse_pct_v10_minus_v9"),
        "mean_delta_holdout_chi2_per_n_dual_v10_minus_v9": mean_of("delta_holdout_chi2_per_n_dual_v10_minus_v9"),
        "seed_3403": s3403 or {},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "# D4 Winner V9 vs V10 Comparison",
        "",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- seeds_compared: `{summary['n_seeds_compared']}`",
        f"- mean_delta_gap_pp_v10_minus_v9: `{f6(summary['mean_delta_gap_pp_v10_minus_v9'])}`",
        f"- mean_delta_holdout_mond_worse_pct_v10_minus_v9: `{f6(summary['mean_delta_holdout_mond_worse_pct_v10_minus_v9'])}`",
        f"- mean_delta_holdout_chi2_per_n_dual_v10_minus_v9: `{f6(summary['mean_delta_holdout_chi2_per_n_dual_v10_minus_v9'])}`",
        "",
        "## Seed 3403",
        "",
    ]
    if s3403:
        for k in [
            "v9_seed_decision",
            "v10_seed_decision",
            "v9_generalization_gap_pp",
            "v10_generalization_gap_pp",
            "delta_gap_pp_v10_minus_v9",
            "v9_holdout_mond_worse_pct",
            "v10_holdout_mond_worse_pct",
            "v9_holdout_chi2_per_n_dual",
            "v10_holdout_chi2_per_n_dual",
        ]:
            report.append(f"- {k}: `{s3403[k]}`")
    else:
        report.append("- seed 3403 not present in both files")
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"seed_comparison_csv: {(out_dir / 'seed_comparison.csv').as_posix()}")
    print(f"summary_json: {(out_dir / 'summary.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
