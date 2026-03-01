#!/usr/bin/env python3
"""
Analyze GR stability metrics from a sweep summary (housekeeping only).

Purpose:
- Quantify stability of G13/G14 drifts and related GR-chain outcomes.
- Provide reproducible diagnostics without changing formulas/thresholds.

Input:
- summary CSV from run_qng_phi_scale_sweep_v1.py (or equivalent schema).

Outputs:
- dataset_stats.csv
- worst_cases.csv
- report.md
- run-log.txt
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY_CSV = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-regression-baseline-v1"
    / "source_runs_grid20"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stability-v1"
)


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    sort_abs: bool


METRICS: list[MetricSpec] = [
    MetricSpec("g13b_e_cov_drift", "G13b E_cov drift", True),
    MetricSpec("g14b_e_cov_drift", "G14b E_cov drift", True),
    MetricSpec("g13c_speed_reduction", "G13c speed reduction", False),
]

OFFICIAL_STATUS_FIELDS = [
    "g10_status",
    "g11_status",
    "g12_status",
    "g13_status",
    "g14_status",
    "g15b_v2_status",
    "g16_status",
]

DIAGNOSTIC_STATUS_FIELDS = [
    "g10_status",
    "g11_status",
    "g12_status",
    "g13_status",
    "g14_status",
    "g15_status",
    "g16_status",
]

STATUS_KEYS = [
    "g13_status",
    "g14_status",
    "g15_status",
    "all_pass_official",
    "all_pass_diagnostic",
    "g16_status",
    "g15b_v2_status",
    "all_pass",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze GR stability diagnostics from summary CSV.")
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--tag", default="gr-ppn-g15b-v2-official")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def mean(values: list[float]) -> float:
    return sum(values) / float(len(values)) if values else float("nan")


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    sorted_vals = sorted(values)
    pos = (len(sorted_vals) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def pass_rate(rows: list[dict[str, str]], key: str) -> float:
    if not rows:
        return float("nan")
    passed = sum(1 for r in rows if r.get(key, "").strip().lower() == "pass")
    return passed / float(len(rows))


def ensure_pass_flags(row: dict[str, str]) -> dict[str, str]:
    out = dict(row)
    if not out.get("all_pass_diagnostic", "").strip():
        diag_ok = all(out.get(k, "").strip().lower() == "pass" for k in DIAGNOSTIC_STATUS_FIELDS)
        out["all_pass_diagnostic"] = "pass" if diag_ok else "fail"
    if not out.get("all_pass_official", "").strip():
        off_ok = all(out.get(k, "").strip().lower() == "pass" for k in OFFICIAL_STATUS_FIELDS)
        out["all_pass_official"] = "pass" if off_ok else "fail"
    if not out.get("all_pass", "").strip():
        out["all_pass"] = out["all_pass_diagnostic"]
    return out


def metric_values(rows: list[dict[str, str]], key: str) -> list[float]:
    out: list[float] = []
    for row in rows:
        v = to_float(row.get(key, ""))
        if v is not None:
            out.append(v)
    return out


def format_float(value: float, digits: int = 6) -> str:
    if value != value:
        return ""
    return f"{value:.{digits}f}"


def build_dataset_stats(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = [ensure_pass_flags(r) for r in rows]
    by_dataset: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_dataset.setdefault(row["dataset_id"], []).append(row)
    by_dataset["ALL"] = rows

    out: list[dict[str, Any]] = []
    for dataset_id in sorted(by_dataset.keys()):
        group = by_dataset[dataset_id]
        rec: dict[str, Any] = {
            "dataset_id": dataset_id,
            "n": len(group),
        }
        for status_key in STATUS_KEYS:
            rec[f"{status_key}_pass_rate"] = format_float(pass_rate(group, status_key), 4)

        g13_vals = metric_values(group, "g13b_e_cov_drift")
        g14_vals = metric_values(group, "g14b_e_cov_drift")
        g13c_vals = metric_values(group, "g13c_speed_reduction")

        rec["g13b_mean"] = format_float(mean(g13_vals))
        rec["g13b_p95"] = format_float(percentile(g13_vals, 0.95))
        rec["g13b_max_abs"] = format_float(max((abs(v) for v in g13_vals), default=float("nan")))

        rec["g14b_mean"] = format_float(mean(g14_vals))
        rec["g14b_p95"] = format_float(percentile(g14_vals, 0.95))
        rec["g14b_max_abs"] = format_float(max((abs(v) for v in g14_vals), default=float("nan")))

        rec["g13c_mean"] = format_float(mean(g13c_vals))
        rec["g13c_p05"] = format_float(percentile(g13c_vals, 0.05))
        rec["g13c_min"] = format_float(min(g13c_vals) if g13c_vals else float("nan"))
        out.append(rec)
    return out


def build_worst_cases(rows: list[dict[str, str]], top_k: int) -> list[dict[str, Any]]:
    rows = [ensure_pass_flags(r) for r in rows]
    out: list[dict[str, Any]] = []
    for metric in METRICS:
        parsed: list[dict[str, Any]] = []
        for row in rows:
            value = to_float(row.get(metric.key, ""))
            if value is None:
                continue
            parsed.append(
                {
                    "dataset_id": row["dataset_id"],
                    "seed": row["seed"],
                    "phi_scale": row["phi_scale"],
                    "value": value,
                    "g13_status": row.get("g13_status", ""),
                    "g14_status": row.get("g14_status", ""),
                    "g15_status": row.get("g15_status", ""),
                    "g16_status": row.get("g16_status", ""),
                    "all_pass": row.get("all_pass", ""),
                }
            )
        if metric.sort_abs:
            parsed.sort(key=lambda r: abs(float(r["value"])), reverse=True)
        else:
            parsed.sort(key=lambda r: float(r["value"]))
        for idx, rec in enumerate(parsed[:top_k], start=1):
            out.append(
                {
                    "metric": metric.key,
                    "metric_label": metric.label,
                    "rank": idx,
                    "dataset_id": rec["dataset_id"],
                    "seed": rec["seed"],
                    "phi_scale": rec["phi_scale"],
                    "value": format_float(float(rec["value"])),
                    "g13_status": rec["g13_status"],
                    "g14_status": rec["g14_status"],
                    "g15_status": rec["g15_status"],
                    "g16_status": rec["g16_status"],
                    "all_pass": rec["all_pass"],
                }
            )
    return out


def write_report(
    path: Path,
    *,
    summary_csv: Path,
    tag: str,
    stats_rows: list[dict[str, Any]],
    worst_rows: list[dict[str, Any]],
) -> None:
    lines: list[str] = []
    lines.append("# GR Stability Report (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    lines.append(f"- freeze_tag: `{tag}`")
    lines.append("")
    lines.append("## Dataset Stats")
    lines.append("")
    lines.append(
        "| dataset | n | all_official | all_diagnostic | g13_pass | g14_pass | "
        "g15_legacy_pass | g16_pass | g15b_v2_pass | g13b_p95 | g14b_p95 | g13c_p05 |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in stats_rows:
        lines.append(
            f"| {r['dataset_id']} | {r['n']} | {r['all_pass_official_pass_rate']} | "
            f"{r['all_pass_diagnostic_pass_rate']} | {r['g13_status_pass_rate']} | "
            f"{r['g14_status_pass_rate']} | {r['g15_status_pass_rate']} | {r['g16_status_pass_rate']} | "
            f"{r['g15b_v2_status_pass_rate']} | {r['g13b_p95']} | {r['g14b_p95']} | {r['g13c_p05']} |"
        )
    lines.append("")
    lines.append("## Worst-Case Rows")
    lines.append("")
    lines.append("| metric | rank | dataset | seed | phi | value | all_pass |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in worst_rows:
        lines.append(
            f"| {r['metric']} | {r['rank']} | {r['dataset_id']} | {r['seed']} | {r['phi_scale']} | {r['value']} | {r['all_pass']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        print(f"[error] summary CSV not found: {summary_csv}")
        return 2

    rows = read_rows(summary_csv)
    if not rows:
        print(f"[error] summary CSV has no rows: {summary_csv}")
        return 2

    stats_rows = build_dataset_stats(rows)
    worst_rows = build_worst_cases(rows, top_k=max(1, args.top_k))

    stats_csv = out_dir / "dataset_stats.csv"
    write_csv(
        stats_csv,
        stats_rows,
        [
            "dataset_id",
            "n",
            "all_pass_official_pass_rate",
            "all_pass_diagnostic_pass_rate",
            "all_pass_pass_rate",
            "g13_status_pass_rate",
            "g14_status_pass_rate",
            "g15_status_pass_rate",
            "g16_status_pass_rate",
            "g15b_v2_status_pass_rate",
            "g13b_mean",
            "g13b_p95",
            "g13b_max_abs",
            "g14b_mean",
            "g14b_p95",
            "g14b_max_abs",
            "g13c_mean",
            "g13c_p05",
            "g13c_min",
        ],
    )

    worst_csv = out_dir / "worst_cases.csv"
    write_csv(
        worst_csv,
        worst_rows,
        [
            "metric",
            "metric_label",
            "rank",
            "dataset_id",
            "seed",
            "phi_scale",
            "value",
            "g13_status",
            "g14_status",
            "g15_status",
            "g16_status",
            "all_pass",
        ],
    )

    report_md = out_dir / "report.md"
    write_report(
        report_md,
        summary_csv=summary_csv,
        tag=args.tag,
        stats_rows=stats_rows,
        worst_rows=worst_rows,
    )

    run_log = out_dir / "run-log-gr-stability.txt"
    run_log.write_text(
        "\n".join(
            [
                "GR stability diagnostics v1",
                f"generated_utc={datetime.utcnow().isoformat()}Z",
                f"source_summary={summary_csv.as_posix()}",
                f"rows={len(rows)}",
                f"top_k={max(1, args.top_k)}",
                f"dataset_stats_csv={stats_csv.as_posix()}",
                f"worst_cases_csv={worst_csv.as_posix()}",
                f"report_md={report_md.as_posix()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"dataset_stats: {stats_csv}")
    print(f"worst_cases:   {worst_csv}")
    print(f"report:        {report_md}")
    print(f"run_log:       {run_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
