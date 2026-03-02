#!/usr/bin/env python3
"""
Analyze GR Stage-2 failures (G11/G12) and build a taxonomy package.

Housekeeping scope:
- no gate formula/threshold edits
- read existing Stage-2 summary and per-run metric CSVs
- emit taxonomy CSVs + markdown report
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-failure-taxonomy-v1"
)


@dataclass(frozen=True)
class GateMetric:
    status: str
    value: float | None
    threshold_text: str
    threshold_op: str
    threshold_value: float | None
    margin: float | None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze GR Stage-2 failures (G11/G12).")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=5)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def f6(v: float | None) -> str:
    if v is None:
        return ""
    if math.isnan(v):
        return ""
    return f"{v:.6f}"


def parse_threshold(text: str) -> tuple[str, float | None]:
    s = (text or "").strip()
    if not s:
        return "", None
    op = ""
    if s.startswith(">="):
        op = ">="
    elif s.startswith("<="):
        op = "<="
    elif s.startswith(">"):
        op = ">"
    elif s.startswith("<"):
        op = "<"
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not m:
        return op, None
    return op, float(m.group(0))


def compute_margin(value: float | None, op: str, thr: float | None) -> float | None:
    if value is None or thr is None:
        return None
    if op in (">", ">="):
        return value - thr
    if op in ("<", "<="):
        return thr - value
    return None


def parse_metric_csv(path: Path) -> dict[str, GateMetric]:
    rows = read_csv(path) if path.exists() else []
    out: dict[str, GateMetric] = {}
    for row in rows:
        gid = (row.get("gate_id") or "").strip()
        if not gid:
            continue
        status = ((row.get("status") or "").strip().lower())
        value = to_float(row.get("value", ""))
        thr_txt = (row.get("threshold") or "").strip()
        op, thr_val = parse_threshold(thr_txt)
        margin = compute_margin(value, op, thr_val)
        out[gid] = GateMetric(
            status=status,
            value=value,
            threshold_text=thr_txt,
            threshold_op=op,
            threshold_value=thr_val,
            margin=margin,
        )
    return out


def get_signature(status_map: dict[str, str], keys: list[str]) -> str:
    failed = [k for k in keys if status_map.get(k, "fail") != "pass"]
    if not failed:
        return "none"
    return "+".join(failed)


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def median(values: list[float]) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    n = len(xs)
    mid = n // 2
    if n % 2 == 1:
        return xs[mid]
    return 0.5 * (xs[mid - 1] + xs[mid])


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        k = str(r.get(key, ""))
        out[k] = out.get(k, 0) + 1
    return out


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    summary_rows = read_csv(summary_csv)
    if not summary_rows:
        raise RuntimeError("summary has zero rows")

    g11_rows: list[dict[str, Any]] = []
    g12_rows: list[dict[str, Any]] = []

    for row in summary_rows:
        run_root = (ROOT / row["run_root"]).resolve()
        g11_metrics = parse_metric_csv(run_root / "g11" / "metric_checks_einstein_eq.csv")
        g12_metrics = parse_metric_csv(run_root / "g12" / "metric_checks_gr_solutions.csv")

        g11_status_map = {
            "G11a": row.get("g11a", "fail"),
            "G11b": row.get("g11b", "fail"),
            "G11c": row.get("g11c", "fail"),
            "G11d": row.get("g11d", "fail"),
        }
        g12_status_map = {
            "G12a": row.get("g12a", "fail"),
            "G12b": row.get("g12b", "fail"),
            "G12c": row.get("g12c", "fail"),
            "G12d": row.get("g12d", "fail"),
        }

        g11_rows.append(
            {
                "dataset_id": row["dataset_id"],
                "seed": row["seed"],
                "g11_status": row.get("g11_status", "fail"),
                "g11_signature": get_signature(g11_status_map, ["G11a", "G11b", "G11c", "G11d"]),
                "g11a_status": g11_status_map["G11a"],
                "g11a_value": f6(g11_metrics.get("G11a", GateMetric("", None, "", "", None, None)).value),
                "g11a_threshold": g11_metrics.get("G11a", GateMetric("", None, "", "", None, None)).threshold_text,
                "g11a_margin": f6(g11_metrics.get("G11a", GateMetric("", None, "", "", None, None)).margin),
                "g11b_status": g11_status_map["G11b"],
                "g11b_value": f6(g11_metrics.get("G11b", GateMetric("", None, "", "", None, None)).value),
                "g11b_threshold": g11_metrics.get("G11b", GateMetric("", None, "", "", None, None)).threshold_text,
                "g11b_margin": f6(g11_metrics.get("G11b", GateMetric("", None, "", "", None, None)).margin),
                "g11c_status": g11_status_map["G11c"],
                "g11c_value": f6(g11_metrics.get("G11c", GateMetric("", None, "", "", None, None)).value),
                "g11d_status": g11_status_map["G11d"],
                "g11d_value": f6(g11_metrics.get("G11d", GateMetric("", None, "", "", None, None)).value),
                "run_root": row["run_root"],
            }
        )

        g12_rows.append(
            {
                "dataset_id": row["dataset_id"],
                "seed": row["seed"],
                "g12_status": row.get("g12_status", "fail"),
                "g12_signature": get_signature(g12_status_map, ["G12a", "G12b", "G12c", "G12d"]),
                "g12a_status": g12_status_map["G12a"],
                "g12a_value": f6(g12_metrics.get("G12a", GateMetric("", None, "", "", None, None)).value),
                "g12b_status": g12_status_map["G12b"],
                "g12b_value": f6(g12_metrics.get("G12b", GateMetric("", None, "", "", None, None)).value),
                "g12c_status": g12_status_map["G12c"],
                "g12c_value": f6(g12_metrics.get("G12c", GateMetric("", None, "", "", None, None)).value),
                "g12d_status": g12_status_map["G12d"],
                "g12d_value": f6(g12_metrics.get("G12d", GateMetric("", None, "", "", None, None)).value),
                "g12d_threshold": g12_metrics.get("G12d", GateMetric("", None, "", "", None, None)).threshold_text,
                "g12d_margin": f6(g12_metrics.get("G12d", GateMetric("", None, "", "", None, None)).margin),
                "run_root": row["run_root"],
            }
        )

    g11_fail = [r for r in g11_rows if str(r["g11_status"]).lower() != "pass"]
    g11_pass = [r for r in g11_rows if str(r["g11_status"]).lower() == "pass"]
    g12_fail = [r for r in g12_rows if str(r["g12_status"]).lower() != "pass"]
    g12_pass = [r for r in g12_rows if str(r["g12_status"]).lower() == "pass"]

    write_csv(out_dir / "g11_fail_cases.csv", g11_fail, list(g11_rows[0].keys()))
    write_csv(out_dir / "g11_pass_cases.csv", g11_pass, list(g11_rows[0].keys()))
    write_csv(out_dir / "g12_fail_cases.csv", g12_fail, list(g12_rows[0].keys()))
    write_csv(out_dir / "g12_pass_cases.csv", g12_pass, list(g12_rows[0].keys()))

    pattern_rows: list[dict[str, Any]] = []
    for gate, rows_all, rows_fail, sign_key in [
        ("G11", g11_rows, g11_fail, "g11_signature"),
        ("G12", g12_rows, g12_fail, "g12_signature"),
    ]:
        ds_totals = count_by(rows_all, "dataset_id")
        ds_fails = count_by(rows_fail, "dataset_id")
        for ds, total in sorted(ds_totals.items()):
            n_fail = ds_fails.get(ds, 0)
            pattern_rows.append(
                {
                    "gate": gate,
                    "dataset_id": ds,
                    "n_total": total,
                    "n_fail": n_fail,
                    "fail_rate": f"{(n_fail / total):.6f}",
                    "signature": "ALL",
                    "count": n_fail,
                }
            )
            sub = [r for r in rows_fail if r["dataset_id"] == ds]
            sig_counts = count_by(sub, sign_key)
            for sig, cnt in sorted(sig_counts.items(), key=lambda kv: (-kv[1], kv[0])):
                pattern_rows.append(
                    {
                        "gate": gate,
                        "dataset_id": ds,
                        "n_total": total,
                        "n_fail": n_fail,
                        "fail_rate": f"{(n_fail / total):.6f}",
                        "signature": sig,
                        "count": cnt,
                    }
                )

    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        ["gate", "dataset_id", "n_total", "n_fail", "fail_rate", "signature", "count"],
    )

    g11a_margins = [abs(to_float(r["g11a_margin"]) or 0.0) for r in g11_fail if r["g11a_status"] != "pass" and r["g11a_margin"] != ""]
    g12d_margins = [abs(to_float(r["g12d_margin"]) or 0.0) for r in g12_fail if r["g12d_status"] != "pass" and r["g12d_margin"] != ""]
    g11_sign = sorted(count_by(g11_fail, "g11_signature").items(), key=lambda kv: (-kv[1], kv[0]))
    g12_sign = sorted(count_by(g12_fail, "g12_signature").items(), key=lambda kv: (-kv[1], kv[0]))

    lines: list[str] = []
    lines.append("# GR Stage-2 Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    lines.append(f"- profiles: `{len(summary_rows)}`")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- `G11` fail: `{len(g11_fail)}/{len(g11_rows)}`")
    lines.append(f"- `G12` fail: `{len(g12_fail)}/{len(g12_rows)}`")
    lines.append("")
    lines.append("## Signature Patterns")
    lines.append("")
    lines.append("### G11")
    lines.append("")
    if not g11_sign:
        lines.append("- no fail signatures")
    else:
        for sig, cnt in g11_sign[: max(1, args.top_k)]:
            lines.append(f"- `{sig}`: `{cnt}`")
    lines.append("")
    lines.append("### G12")
    lines.append("")
    if not g12_sign:
        lines.append("- no fail signatures")
    else:
        for sig, cnt in g12_sign[: max(1, args.top_k)]:
            lines.append(f"- `{sig}`: `{cnt}`")
    lines.append("")
    lines.append("## Margin Diagnostics")
    lines.append("")
    lines.append("| metric | n | mean_abs_margin | median_abs_margin |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(f"| G11a fail margin | {len(g11a_margins)} | {f6(mean(g11a_margins))} | {f6(median(g11a_margins))} |")
    lines.append(f"| G12d fail margin | {len(g12d_margins)} | {f6(mean(g12d_margins))} | {f6(median(g12d_margins))} |")
    lines.append("")
    lines.append("## Candidate v2 Prereg Direction (no v1 change)")
    lines.append("")
    lines.append("1. Keep v1 gates unchanged as official Stage-2 baseline.")
    lines.append("2. Add candidate-only estimators:")
    lines.append("   - `G11a-v2-candidate`: robustness to weak linearity regimes (rank/robust trend diagnostic).")
    lines.append("   - `G12d-v2-candidate`: robust radial-decay slope diagnostic (trimmed/bin-stable slope).")
    lines.append("3. Evaluate candidate-only on fixed grid (`DS-002/003/006`, seeds `3401..3600`) plus holdout seed block before any promotion.")
    lines.append("4. Promotion rule should use non-degradation vs v1 + minimum uplift, pre-registered before reruns.")
    lines.append("")

    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"g11_fail_cases:  {out_dir / 'g11_fail_cases.csv'}")
    print(f"g12_fail_cases:  {out_dir / 'g12_fail_cases.csv'}")
    print(f"pattern_summary: {out_dir / 'pattern_summary.csv'}")
    print(f"report_md:       {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
