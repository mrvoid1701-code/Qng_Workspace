#!/usr/bin/env python3
"""
Evaluate frozen promotion criteria for G16b hybrid candidate.

Inputs:
- summary.csv from scripts/tools/run_g16b_split_hybrid_v1.py

Outputs:
- report.md
- report.json
- dataset_summary.csv

No gate logic is changed. This script only applies preregistered acceptance rules.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-hybrid-promotion-eval-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate G16b hybrid promotion criteria (v1).")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="g16b-hybrid-promotion-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--min-global-uplift-pp", type=float, default=2.0)
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-per-dataset-nondegrade", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-high-signal-nondegrade", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-low-signal-improvement", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def norm_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


@dataclass(frozen=True)
class Totals:
    n: int
    v1_pass: int
    hybrid_pass: int
    improved: int
    degraded: int

    @property
    def v1_fail(self) -> int:
        return self.n - self.v1_pass

    @property
    def hybrid_fail(self) -> int:
        return self.n - self.hybrid_pass

    @property
    def uplift_pp(self) -> float:
        if self.n == 0:
            return 0.0
        return 100.0 * (self.hybrid_pass - self.v1_pass) / self.n


def compute_totals(rows: list[dict[str, str]]) -> Totals:
    n = len(rows)
    v1_pass = sum(1 for r in rows if norm_status(r.get("g16b_v1_status", "")) == "pass")
    hybrid_pass = sum(1 for r in rows if norm_status(r.get("g16b_hybrid_status", "")) == "pass")
    improved = sum(
        1
        for r in rows
        if norm_status(r.get("g16b_v1_status", "")) == "fail"
        and norm_status(r.get("g16b_hybrid_status", "")) == "pass"
    )
    degraded = sum(
        1
        for r in rows
        if norm_status(r.get("g16b_v1_status", "")) == "pass"
        and norm_status(r.get("g16b_hybrid_status", "")) == "fail"
    )
    return Totals(n=n, v1_pass=v1_pass, hybrid_pass=hybrid_pass, improved=improved, degraded=degraded)


def bool_str(v: bool) -> str:
    return "true" if v else "false"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary csv not found: {summary_csv}")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has no rows")

    strict_datasets = [d.upper() for d in parse_csv_list(args.strict_datasets)]
    datasets = sorted({(r.get("dataset_id", "").strip().upper()) for r in rows if r.get("dataset_id", "").strip()})
    if strict_datasets and datasets != sorted(strict_datasets):
        raise ValueError(f"strict dataset mismatch: expected {sorted(strict_datasets)}, got {datasets}")

    overall = compute_totals(rows)

    ds_rows: list[dict[str, Any]] = []
    per_dataset_ok = True
    for ds in datasets:
        sub = [r for r in rows if r.get("dataset_id", "").strip().upper() == ds]
        t = compute_totals(sub)
        ok = t.hybrid_pass >= t.v1_pass
        per_dataset_ok = per_dataset_ok and ok
        ds_rows.append(
            {
                "dataset_id": ds,
                "n": t.n,
                "v1_pass": t.v1_pass,
                "v1_fail": t.v1_fail,
                "hybrid_pass": t.hybrid_pass,
                "hybrid_fail": t.hybrid_fail,
                "improved": t.improved,
                "degraded": t.degraded,
                "uplift_pp": f"{t.uplift_pp:.3f}",
                "nondegrade_pass": bool_str(ok),
            }
        )

    low_rows = [r for r in rows if (r.get("signal_regime", "").strip().lower() == "low" or r.get("is_low_signal", "").strip().lower() == "true")]
    high_rows = [r for r in rows if (r.get("signal_regime", "").strip().lower() == "high" or r.get("is_low_signal", "").strip().lower() == "false")]
    low_tot = compute_totals(low_rows)
    high_tot = compute_totals(high_rows)

    c_zero_degraded = overall.degraded == 0
    c_per_dataset = per_dataset_ok
    c_high_nondegrade = high_tot.hybrid_fail <= high_tot.v1_fail
    c_low_improve = low_tot.hybrid_fail < low_tot.v1_fail
    c_global_uplift = overall.uplift_pp >= args.min_global_uplift_pp

    checks = {
        "zero_degraded": (not args.require_zero_degraded) or c_zero_degraded,
        "per_dataset_nondegrade": (not args.require_per_dataset_nondegrade) or c_per_dataset,
        "high_signal_nondegrade": (not args.require_high_signal_nondegrade) or c_high_nondegrade,
        "low_signal_improvement": (not args.require_low_signal_improvement) or c_low_improve,
        "global_uplift_min": c_global_uplift,
    }
    decision = all(checks.values())

    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()) if ds_rows else ["dataset_id"])

    report_json = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "input_summary_csv": summary_csv.as_posix(),
        "datasets": datasets,
        "criteria": {
            "min_global_uplift_pp": args.min_global_uplift_pp,
            "require_zero_degraded": args.require_zero_degraded,
            "require_per_dataset_nondegrade": args.require_per_dataset_nondegrade,
            "require_high_signal_nondegrade": args.require_high_signal_nondegrade,
            "require_low_signal_improvement": args.require_low_signal_improvement,
        },
        "overall": {
            "n": overall.n,
            "v1_pass": overall.v1_pass,
            "v1_fail": overall.v1_fail,
            "hybrid_pass": overall.hybrid_pass,
            "hybrid_fail": overall.hybrid_fail,
            "improved": overall.improved,
            "degraded": overall.degraded,
            "uplift_pp": round(overall.uplift_pp, 6),
        },
        "low_signal": {
            "n": low_tot.n,
            "v1_fail": low_tot.v1_fail,
            "hybrid_fail": low_tot.hybrid_fail,
        },
        "high_signal": {
            "n": high_tot.n,
            "v1_fail": high_tot.v1_fail,
            "hybrid_fail": high_tot.hybrid_fail,
        },
        "per_dataset": ds_rows,
        "checks": {k: bool(v) for k, v in checks.items()},
        "decision": "PASS" if decision else "FAIL",
    }
    (out_dir / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# G16b Hybrid Promotion Evaluation (v1)")
    lines.append("")
    lines.append(f"- eval_id: `{args.eval_id}`")
    lines.append(f"- generated_utc: `{report_json['generated_utc']}`")
    lines.append(f"- input_summary_csv: `{summary_csv.as_posix()}`")
    lines.append(f"- decision: `{'PASS' if decision else 'FAIL'}`")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(
        f"- n={overall.n}, v1_pass={overall.v1_pass}, hybrid_pass={overall.hybrid_pass}, "
        f"improved={overall.improved}, degraded={overall.degraded}, uplift_pp={overall.uplift_pp:.3f}"
    )
    lines.append("")
    lines.append("## Criteria Checks")
    lines.append("")
    lines.append(f"- zero_degraded: {bool_str(checks['zero_degraded'])}")
    lines.append(f"- per_dataset_nondegrade: {bool_str(checks['per_dataset_nondegrade'])}")
    lines.append(f"- high_signal_nondegrade: {bool_str(checks['high_signal_nondegrade'])}")
    lines.append(f"- low_signal_improvement: {bool_str(checks['low_signal_improvement'])}")
    lines.append(f"- global_uplift_min({args.min_global_uplift_pp:.3f}pp): {bool_str(checks['global_uplift_min'])}")
    lines.append("")
    lines.append("## Regime Summary")
    lines.append("")
    lines.append(f"- low_signal: n={low_tot.n}, v1_fail={low_tot.v1_fail}, hybrid_fail={low_tot.hybrid_fail}")
    lines.append(f"- high_signal: n={high_tot.n}, v1_fail={high_tot.v1_fail}, hybrid_fail={high_tot.hybrid_fail}")
    lines.append("")
    lines.append("## Per-Dataset")
    lines.append("")
    lines.append("| dataset | n | v1_pass | hybrid_pass | uplift_pp | degraded | nondegrade_pass |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in ds_rows:
        lines.append(
            f"| {row['dataset_id']} | {row['n']} | {row['v1_pass']} | {row['hybrid_pass']} | "
            f"{row['uplift_pp']} | {row['degraded']} | {row['nondegrade_pass']} |"
        )
    lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {dataset_csv}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

