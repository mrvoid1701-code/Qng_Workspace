#!/usr/bin/env python3
"""Evaluate prereg promotion checks for Stage-2 G11a-v3 candidate."""

from __future__ import annotations

import argparse
import csv
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
    / "gr-stage2-g11-v3-promotion-eval-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-2 G11a-v3 promotion checks.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="gr-stage2-g11-v3-promotion-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--min-improved", type=int, default=5)
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-per-dataset-nondegrade", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--min-weak-corr-drop", type=int, default=2)
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def bool_str(v: bool) -> str:
    return "true" if v else "false"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")
    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary has zero rows")

    strict_datasets = sorted([d.upper() for d in parse_csv_list(args.strict_datasets)])
    datasets = sorted({str(r.get("dataset_id", "")).strip().upper() for r in rows if str(r.get("dataset_id", "")).strip()})
    if strict_datasets and datasets != strict_datasets:
        raise ValueError(f"strict dataset mismatch: expected {strict_datasets}, got {datasets}")

    n = len(rows)
    v2_pass = sum(1 for r in rows if norm_status(r.get("g11_v2_status", "")) == "pass")
    v3_pass = sum(1 for r in rows if norm_status(r.get("g11_v3_status", "")) == "pass")
    improved = sum(1 for r in rows if norm_status(r.get("g11_v2_status", "")) == "fail" and norm_status(r.get("g11_v3_status", "")) == "pass")
    degraded = sum(1 for r in rows if norm_status(r.get("g11_v2_status", "")) == "pass" and norm_status(r.get("g11_v3_status", "")) == "fail")

    weak_v2 = sum(1 for r in rows if norm_status(r.get("g11_v2_status", "")) == "fail" and str(r.get("g11_v2_weak_corr_flag", "")).strip().lower() == "true")
    weak_v3 = sum(1 for r in rows if norm_status(r.get("g11_v3_status", "")) == "fail" and str(r.get("g11_v3_weak_corr_flag", "")).strip().lower() == "true")
    weak_drop = weak_v2 - weak_v3

    per_ds_rows: list[dict[str, Any]] = []
    per_ds_ok = True
    for ds in datasets:
        sub = [r for r in rows if str(r.get("dataset_id", "")).strip().upper() == ds]
        ds_n = len(sub)
        ds_v2_pass = sum(1 for r in sub if norm_status(r.get("g11_v2_status", "")) == "pass")
        ds_v3_pass = sum(1 for r in sub if norm_status(r.get("g11_v3_status", "")) == "pass")
        ds_improved = sum(1 for r in sub if norm_status(r.get("g11_v2_status", "")) == "fail" and norm_status(r.get("g11_v3_status", "")) == "pass")
        ds_degraded = sum(1 for r in sub if norm_status(r.get("g11_v2_status", "")) == "pass" and norm_status(r.get("g11_v3_status", "")) == "fail")
        ds_nondegrade = ds_v3_pass >= ds_v2_pass
        per_ds_ok = per_ds_ok and ds_nondegrade
        per_ds_rows.append(
            {
                "dataset_id": ds,
                "n": ds_n,
                "g11_v2_pass": ds_v2_pass,
                "g11_v3_pass": ds_v3_pass,
                "improved": ds_improved,
                "degraded": ds_degraded,
                "nondegrade_pass": bool_str(ds_nondegrade),
            }
        )

    checks = {
        "zero_degraded": (not args.require_zero_degraded) or (degraded == 0),
        "improved_min": improved >= max(0, args.min_improved),
        "per_dataset_nondegrade": (not args.require_per_dataset_nondegrade) or per_ds_ok,
        "weak_corr_drop_min": weak_drop >= max(0, args.min_weak_corr_drop),
    }
    decision = all(checks.values())

    write_csv(
        out_dir / "dataset_summary.csv",
        per_ds_rows,
        ["dataset_id", "n", "g11_v2_pass", "g11_v3_pass", "improved", "degraded", "nondegrade_pass"],
    )

    report_json = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": summary_csv.as_posix(),
        "datasets": datasets,
        "criteria": {
            "min_improved": args.min_improved,
            "require_zero_degraded": args.require_zero_degraded,
            "require_per_dataset_nondegrade": args.require_per_dataset_nondegrade,
            "min_weak_corr_drop": args.min_weak_corr_drop,
        },
        "totals": {
            "n": n,
            "g11_v2_pass": v2_pass,
            "g11_v3_pass": v3_pass,
            "improved": improved,
            "degraded": degraded,
            "weak_corr_fail_count_v2": weak_v2,
            "weak_corr_fail_count_v3": weak_v3,
            "weak_corr_drop": weak_drop,
        },
        "checks": checks,
        "decision": "PASS" if decision else "FAIL",
    }
    (out_dir / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    lines = [
        "# GR Stage-2 G11a-v3 Promotion Evaluation (v1)",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report_json['generated_utc']}`",
        f"- source_summary_csv: `{summary_csv.as_posix()}`",
        f"- decision: `{'PASS' if decision else 'FAIL'}`",
        "",
        "## Totals",
        "",
        f"- g11_v2_pass: `{v2_pass}/{n}`",
        f"- g11_v3_pass: `{v3_pass}/{n}`",
        f"- improved_vs_v2: `{improved}`",
        f"- degraded_vs_v2: `{degraded}`",
        f"- weak_corr_fail_count_v2: `{weak_v2}`",
        f"- weak_corr_fail_count_v3: `{weak_v3}`",
        f"- weak_corr_drop: `{weak_drop}`",
        "",
        "## Checks",
        "",
        f"- zero_degraded: `{bool_str(checks['zero_degraded'])}`",
        f"- improved_min: `{bool_str(checks['improved_min'])}` (min={args.min_improved})",
        f"- per_dataset_nondegrade: `{bool_str(checks['per_dataset_nondegrade'])}`",
        f"- weak_corr_drop_min: `{bool_str(checks['weak_corr_drop_min'])}` (min={args.min_weak_corr_drop})",
        "",
        "## Dataset Summary",
        "",
        "| dataset | n | g11_v2_pass | g11_v3_pass | improved | degraded | nondegrade_pass |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in per_ds_rows:
        lines.append(
            f"| {r['dataset_id']} | {r['n']} | {r['g11_v2_pass']} | {r['g11_v3_pass']} | "
            f"{r['improved']} | {r['degraded']} | {r['nondegrade_pass']} |"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
