#!/usr/bin/env python3
"""Build QM Stage-1 regression baseline JSON from official summary + promotion artifacts."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qm-stage1-regression-baseline-v1"

BLOCK_DEFAULTS = {
    "primary": {
        "summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-stage1-official-v2"
        / "primary_ds002_003_006_s3401_3600"
        / "summary.csv",
        "metrics_summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-candidate-v2"
        / "primary_ds002_003_006_s3401_3600"
        / "summary.csv",
        "promotion_report_json": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-promotion-eval-v1"
        / "primary_ds002_003_006_s3401_3600"
        / "report.json",
        "out_json": BASELINE_DIR / "qm_stage1_baseline_primary.json",
        "baseline_id": "qm-stage1-baseline-primary-v1",
    },
    "attack": {
        "summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-stage1-official-v2"
        / "attack_seed500_ds002_003_006_s3601_4100"
        / "summary.csv",
        "metrics_summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-candidate-v2"
        / "attack_seed500_ds002_003_006_s3601_4100"
        / "summary.csv",
        "promotion_report_json": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-promotion-eval-v1"
        / "attack_seed500_ds002_003_006_s3601_4100"
        / "report.json",
        "out_json": BASELINE_DIR / "qm_stage1_baseline_attack.json",
        "baseline_id": "qm-stage1-baseline-attack-v1",
    },
    "holdout": {
        "summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-stage1-official-v2"
        / "attack_holdout_ds004_008_s3401_3600"
        / "summary.csv",
        "metrics_summary_csv": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-candidate-v2"
        / "attack_holdout_ds004_008_s3401_3600"
        / "summary.csv",
        "promotion_report_json": ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "qm-g17-promotion-eval-v1"
        / "attack_holdout_ds004_008_s3401_3600"
        / "report.json",
        "out_json": BASELINE_DIR / "qm_stage1_baseline_holdout.json",
        "baseline_id": "qm-stage1-baseline-holdout-v1",
    },
}

DEFAULT_OFFICIAL_STATUS_FIELDS = [
    "g17_status",
    "g18_status",
    "g19_status",
    "g20_status",
    "all_pass_qm_lane",
]
DEFAULT_SUBGATE_STATUS_FIELDS = [
    "g17a_status_v2",
    "g17b_status",
    "g17c_status",
    "g17d_status",
]


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build QM Stage-1 baseline JSON (v1).")
    p.add_argument("--block", choices=("primary", "attack", "holdout"), required=True)
    p.add_argument("--summary-csv", default="")
    p.add_argument("--metrics-summary-csv", default="")
    p.add_argument("--promotion-report-json", default="")
    p.add_argument("--out-json", default="")
    p.add_argument("--baseline-id", default="")
    p.add_argument("--effective-tag", default="qm-stage1-g17-v2-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument("--official-status-fields", default=",".join(DEFAULT_OFFICIAL_STATUS_FIELDS))
    p.add_argument("--subgate-status-fields", default=",".join(DEFAULT_SUBGATE_STATUS_FIELDS))
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def norm_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


def to_number(raw: Any) -> float | None:
    txt = str(raw or "").strip().lower()
    if txt == "":
        return None
    if txt in {"true", "false"}:
        return 1.0 if txt == "true" else 0.0
    try:
        value = float(txt)
    except ValueError:
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("percentile requires non-empty values")
    if len(values) == 1:
        return values[0]
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    w = pos - lo
    return s[lo] + (s[hi] - s[lo]) * w


def detect_status_fields(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    cols = list(rows[0].keys())
    out: list[str] = []
    for col in cols:
        if ("_status" in col) or col.startswith("all_pass_qm_lane"):
            out.append(col)
    return out


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def detect_numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    excluded = {
        "dataset_id",
        "seed",
        "run_root",
        "policy_id",
        "source_policy_id",
        "g17a_v2_rule",
    }
    out: list[str] = []
    cols = list(rows[0].keys())
    for col in cols:
        if col in excluded:
            continue
        if col.endswith("_status") or col.startswith("all_pass_qm_lane"):
            continue
        has_number = False
        for r in rows:
            if to_number(r.get(col, "")) is not None:
                has_number = True
                break
        if has_number:
            out.append(col)
    return out


def status_pass_rates(rows: list[dict[str, str]], fields: list[str]) -> dict[str, dict[str, Any]]:
    n = len(rows)
    out: dict[str, dict[str, Any]] = {}
    for field in fields:
        pass_count = sum(1 for r in rows if norm_status(r.get(field, "")) == "pass")
        out[field] = {
            "pass": pass_count,
            "total": n,
            "pass_rate": (pass_count / n) if n else 0.0,
        }
    return out


def metric_stats(
    official_rows: list[dict[str, str]],
    metrics_rows: list[dict[str, str]],
    metric_fields: list[str],
) -> tuple[dict[str, dict[str, Any]], int]:
    if not metric_fields:
        return {}, 0
    metrics_map: dict[str, dict[str, str]] = {}
    for r in metrics_rows:
        try:
            k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
        except Exception:
            continue
        metrics_map[k] = r

    matched = 0
    collected: dict[str, list[float]] = {f: [] for f in metric_fields}
    for r in official_rows:
        k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
        mr = metrics_map.get(k)
        if mr is None:
            continue
        matched += 1
        for f in metric_fields:
            val = to_number(mr.get(f, ""))
            if val is not None:
                collected[f].append(val)

    out: dict[str, dict[str, Any]] = {}
    for f in metric_fields:
        vals = collected[f]
        if not vals:
            continue
        out[f] = {
            "count": len(vals),
            "min": round(min(vals), 12),
            "median": round(percentile(vals, 0.5), 12),
            "p95": round(percentile(vals, 0.95), 12),
        }
    return out, matched


def main() -> int:
    args = parse_args()
    defaults = BLOCK_DEFAULTS[args.block]

    summary_csv = Path(args.summary_csv).resolve() if args.summary_csv else Path(defaults["summary_csv"]).resolve()
    metrics_summary_csv = (
        Path(args.metrics_summary_csv).resolve()
        if args.metrics_summary_csv
        else Path(defaults["metrics_summary_csv"]).resolve()
    )
    promotion_report_json = (
        Path(args.promotion_report_json).resolve()
        if args.promotion_report_json
        else Path(defaults["promotion_report_json"]).resolve()
    )
    out_json = Path(args.out_json).resolve() if args.out_json else Path(defaults["out_json"]).resolve()
    baseline_id = args.baseline_id.strip() or str(defaults["baseline_id"])

    if not summary_csv.exists():
        raise FileNotFoundError(f"official summary missing: {summary_csv}")

    official_rows = read_csv(summary_csv)
    if not official_rows:
        raise RuntimeError(f"official summary has zero rows: {summary_csv}")
    official_rows.sort(key=lambda r: (str(r.get("dataset_id", "")), int(str(r.get("seed", "0")))))

    status_detected = detect_status_fields(official_rows)
    official_fields = [f for f in parse_csv_list(args.official_status_fields) if f in status_detected]
    subgate_fields = [f for f in parse_csv_list(args.subgate_status_fields) if f in status_detected]
    all_status_fields = unique_keep_order(official_fields + subgate_fields + status_detected)

    profiles: list[dict[str, Any]] = []
    for r in official_rows:
        ds = str(r.get("dataset_id", "")).strip()
        seed = int(str(r.get("seed", "0")))
        profiles.append({"dataset_id": ds, "seed": seed})

    metrics_source_rows: list[dict[str, str]]
    metrics_source_csv: Path
    if metrics_summary_csv.exists():
        metrics_source_rows = read_csv(metrics_summary_csv)
        metrics_source_csv = metrics_summary_csv
    else:
        metrics_source_rows = official_rows
        metrics_source_csv = summary_csv

    numeric_fields = detect_numeric_fields(metrics_source_rows)
    numeric_stats, matched_metric_profiles = metric_stats(official_rows, metrics_source_rows, numeric_fields)
    missing_metric_profiles = len(official_rows) - matched_metric_profiles

    promotion_payload: dict[str, Any] = {}
    if promotion_report_json.exists():
        promotion_payload = json.loads(promotion_report_json.read_text(encoding="utf-8"))

    baseline = {
        "baseline_id": baseline_id,
        "block_id": args.block,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "notes": [
            "QM Stage-1 baseline generated from official governance summary.",
            "Guard decision uses official pass-rate non-degradation + profile-set match.",
            "Numeric metric stats are descriptive and sourced from metrics summary when available.",
        ],
        "sources": {
            "official_summary_csv": summary_csv.as_posix(),
            "metrics_summary_csv": metrics_source_csv.as_posix(),
            "promotion_report_json": promotion_report_json.as_posix() if promotion_report_json.exists() else "",
        },
        "profiles": profiles,
        "compare": {
            "official_status_fields": official_fields,
            "subgate_status_fields": subgate_fields,
            "status_fields": all_status_fields,
            "numeric_metric_fields": sorted(list(numeric_stats.keys())),
        },
        "pass_rates": {
            "official": status_pass_rates(official_rows, official_fields),
            "subgates": status_pass_rates(official_rows, subgate_fields),
            "all_status_fields": status_pass_rates(official_rows, all_status_fields),
        },
        "numeric_metrics": numeric_stats,
        "metrics_coverage": {
            "profiles_total": len(official_rows),
            "profiles_with_metrics": matched_metric_profiles,
            "profiles_missing_metrics": missing_metric_profiles,
        },
        "promotion_eval": {
            "eval_id": promotion_payload.get("eval_id", ""),
            "overall_decision": promotion_payload.get("overall_decision", ""),
            "criteria": promotion_payload.get("criteria", {}),
            "g17_totals": (promotion_payload.get("g17", {}) or {}).get("totals", {}),
            "qm_lane_totals": (promotion_payload.get("qm_lane", {}) or {}).get("totals", {}),
        },
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"wrote: {out_json}")
    print(f"profiles: {len(profiles)}")
    print(f"official_status_fields: {len(official_fields)}")
    print(f"subgate_status_fields: {len(subgate_fields)}")
    print(f"numeric_metric_fields: {len(numeric_stats)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
