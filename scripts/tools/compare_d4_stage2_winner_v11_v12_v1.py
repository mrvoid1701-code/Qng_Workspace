#!/usr/bin/env python3
"""Compare D4 winner v11 vs v12 strict outcomes per split seed."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_V11 = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v11-strict"
    / "evaluation-v1"
    / "per_seed_evaluation.csv"
)
DEFAULT_V12 = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v12-strict"
    / "evaluation-v1"
    / "per_seed_evaluation.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v12-strict"
    / "comparison-v11-v12-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare per-seed strict evaluation between D4 winner v11 and v12.")
    p.add_argument("--v11-csv", default=str(DEFAULT_V11))
    p.add_argument("--v12-csv", default=str(DEFAULT_V12))
    p.add_argument("--strict-coverage", action=argparse.BooleanOptionalAction, default=True)
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
    v11_path = Path(args.v11_csv).resolve()
    v12_path = Path(args.v12_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    v11_rows = read_csv(v11_path)
    v12_rows = read_csv(v12_path)
    v11_by_seed = {int(r["split_seed"]): r for r in v11_rows}
    v12_by_seed = {int(r["split_seed"]): r for r in v12_rows}
    v11_seed_set = set(v11_by_seed.keys())
    v12_seed_set = set(v12_by_seed.keys())
    seeds = sorted(v11_seed_set & v12_seed_set)
    missing_in_v12 = sorted(v11_seed_set - v12_seed_set)
    missing_in_v11 = sorted(v12_seed_set - v11_seed_set)
    coverage_ok = (len(missing_in_v12) == 0 and len(missing_in_v11) == 0 and len(seeds) > 0)

    cmp_rows: list[dict[str, str]] = []
    for seed in seeds:
        a = v11_by_seed[seed]
        b = v12_by_seed[seed]
        gap_a = float(a["generalization_gap_pp"])
        gap_b = float(b["generalization_gap_pp"])
        mond_a = float(a["holdout_mond_worse_pct"])
        mond_b = float(b["holdout_mond_worse_pct"])
        c2_a = float(a["holdout_chi2_per_n_dual"])
        c2_b = float(b["holdout_chi2_per_n_dual"])
        cmp_rows.append(
            {
                "split_seed": str(seed),
                "v11_seed_decision": str(a["seed_decision"]),
                "v12_seed_decision": str(b["seed_decision"]),
                "v11_generalization_gap_pp": f6(gap_a),
                "v12_generalization_gap_pp": f6(gap_b),
                "delta_gap_pp_v12_minus_v11": f6(gap_b - gap_a),
                "v11_holdout_mond_worse_pct": f6(mond_a),
                "v12_holdout_mond_worse_pct": f6(mond_b),
                "delta_holdout_mond_worse_pct_v12_minus_v11": f6(mond_b - mond_a),
                "v11_holdout_chi2_per_n_dual": f6(c2_a),
                "v12_holdout_chi2_per_n_dual": f6(c2_b),
                "delta_holdout_chi2_per_n_dual_v12_minus_v11": f6(c2_b - c2_a),
            }
        )

    fields = list(cmp_rows[0].keys()) if cmp_rows else []
    write_csv(out_dir / "seed_comparison.csv", cmp_rows, fields)

    def mean_of(key: str) -> float:
        if not cmp_rows:
            return 0.0
        return sum(float(r[key]) for r in cmp_rows) / len(cmp_rows)

    s3403 = next((r for r in cmp_rows if r["split_seed"] == "3403"), None)
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "v11_csv": v11_path.as_posix(),
        "v12_csv": v12_path.as_posix(),
        "strict_coverage": bool(args.strict_coverage),
        "coverage_ok": coverage_ok,
        "missing_in_v12": missing_in_v12,
        "missing_in_v11": missing_in_v11,
        "n_seeds_compared": len(cmp_rows),
        "mean_delta_gap_pp_v12_minus_v11": mean_of("delta_gap_pp_v12_minus_v11"),
        "mean_delta_holdout_mond_worse_pct_v12_minus_v11": mean_of("delta_holdout_mond_worse_pct_v12_minus_v11"),
        "mean_delta_holdout_chi2_per_n_dual_v12_minus_v11": mean_of("delta_holdout_chi2_per_n_dual_v12_minus_v11"),
        "seed_3403": s3403 or {},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "# D4 Winner V11 vs V12 Comparison",
        "",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- coverage_ok: `{summary['coverage_ok']}`",
        f"- missing_in_v12: `{summary['missing_in_v12']}`",
        f"- missing_in_v11: `{summary['missing_in_v11']}`",
        f"- seeds_compared: `{summary['n_seeds_compared']}`",
        f"- mean_delta_gap_pp_v12_minus_v11: `{f6(summary['mean_delta_gap_pp_v12_minus_v11'])}`",
        f"- mean_delta_holdout_mond_worse_pct_v12_minus_v11: `{f6(summary['mean_delta_holdout_mond_worse_pct_v12_minus_v11'])}`",
        f"- mean_delta_holdout_chi2_per_n_dual_v12_minus_v11: `{f6(summary['mean_delta_holdout_chi2_per_n_dual_v12_minus_v11'])}`",
        "",
        "## Seed 3403",
        "",
    ]
    if s3403:
        for k in [
            "v11_seed_decision",
            "v12_seed_decision",
            "v11_holdout_mond_worse_pct",
            "v12_holdout_mond_worse_pct",
            "v11_holdout_chi2_per_n_dual",
            "v12_holdout_chi2_per_n_dual",
            "v11_generalization_gap_pp",
            "v12_generalization_gap_pp",
            "delta_gap_pp_v12_minus_v11",
        ]:
            report.append(f"- {k}: `{s3403[k]}`")
    else:
        report.append("- seed 3403 not present in both files")
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"seed_comparison_csv: {(out_dir / 'seed_comparison.csv').as_posix()}")
    print(f"summary_json: {(out_dir / 'summary.json').as_posix()}")
    if bool(args.strict_coverage) and not coverage_ok:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
