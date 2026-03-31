#!/usr/bin/env python3
"""Build stability official-v2 regression baseline JSON."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "05_validation" / "evidence" / "artifacts"
BASELINE_DIR = BASE / "stability-regression-baseline-v1"

BLOCK_DEFAULTS = {
    "primary": {
        "summary_csv": BASE / "stability-official-v2" / "primary_s3401" / "summary.csv",
        "out_json": BASELINE_DIR / "stability_baseline_primary.json",
        "baseline_id": "stability-baseline-primary-v1",
    },
    "attack": {
        "summary_csv": BASE / "stability-official-v2" / "attack_s3401_4401" / "summary.csv",
        "out_json": BASELINE_DIR / "stability_baseline_attack.json",
        "baseline_id": "stability-baseline-attack-v1",
    },
    "holdout": {
        "summary_csv": BASE / "stability-official-v2" / "holdout_n30_42_s3401" / "summary.csv",
        "out_json": BASELINE_DIR / "stability_baseline_holdout.json",
        "baseline_id": "stability-baseline-holdout-v1",
    },
}

DEFAULT_OFFICIAL_FIELDS = [
    "gate_sigma_bounds",
    "gate_metric_positive",
    "gate_metric_cond",
    "gate_runaway",
    "gate_energy_drift",
    "gate_variational_residual",
    "gate_alpha_drift",
    "gate_no_signalling",
    "all_pass_stability",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build stability baseline JSON (official-v2).")
    p.add_argument("--block", choices=("primary", "attack", "holdout"), required=True)
    p.add_argument("--summary-csv", default="")
    p.add_argument("--out-json", default="")
    p.add_argument("--baseline-id", default="")
    p.add_argument("--effective-tag", default="stability-energy-v2-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument("--official-status-fields", default=",".join(DEFAULT_OFFICIAL_FIELDS))
    return p.parse_args()


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def to_number(v: Any) -> float | None:
    txt = str(v or "").strip().lower()
    if txt == "":
        return None
    if txt in {"true", "false"}:
        return 1.0 if txt == "true" else 0.0
    try:
        x = float(txt)
    except Exception:
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return x


def percentile(vals: list[float], q: float) -> float:
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
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
    return [c for c in cols if c.startswith("gate_") or c.startswith("all_pass")]


def detect_numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    excluded = {
        "dataset_id",
        "combo_id",
        "case_id",
        "case_seed",
        "policy_id",
        "source_policy_id",
        "energy_v2_path",
    }
    out: list[str] = []
    cols = list(rows[0].keys())
    for c in cols:
        if c in excluded:
            continue
        if c.startswith("gate_") or c.startswith("all_pass"):
            continue
        if any(to_number(r.get(c, "")) is not None for r in rows):
            out.append(c)
    return out


def pass_rates(rows: list[dict[str, str]], fields: list[str]) -> dict[str, dict[str, Any]]:
    n = len(rows)
    out: dict[str, dict[str, Any]] = {}
    for f in fields:
        p = sum(1 for r in rows if norm_status(r.get(f, "")) == "pass")
        out[f] = {"pass": p, "total": n, "pass_rate": (p / n if n else 0.0)}
    return out


def key_tuple(r: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(r.get("dataset_id", "")),
        str(r.get("combo_id", "")),
        str(r.get("case_id", "")),
        str(r.get("case_seed", "")),
    )


def main() -> int:
    args = parse_args()
    defaults = BLOCK_DEFAULTS[args.block]
    summary_csv = Path(args.summary_csv).resolve() if args.summary_csv else Path(defaults["summary_csv"]).resolve()
    out_json = Path(args.out_json).resolve() if args.out_json else Path(defaults["out_json"]).resolve()
    baseline_id = args.baseline_id.strip() or str(defaults["baseline_id"])
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary missing: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary has zero rows")
    rows.sort(key=lambda r: key_tuple(r))

    detected_status = detect_status_fields(rows)
    official_fields = [f for f in parse_csv_list(args.official_status_fields) if f in detected_status]
    if not official_fields:
        raise RuntimeError("no official status fields found in summary")

    status_rows: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    for r in rows:
        profiles.append(
            {
                "dataset_id": str(r.get("dataset_id", "")),
                "combo_id": str(r.get("combo_id", "")),
                "case_id": str(r.get("case_id", "")),
                "case_seed": str(r.get("case_seed", "")),
            }
        )
        rec = {k: v for k, v in profiles[-1].items()}
        for f in detected_status:
            rec[f] = norm_status(r.get(f, ""))
        status_rows.append(rec)

    num_fields = detect_numeric_fields(rows)
    metric_stats: dict[str, dict[str, Any]] = {}
    for f in num_fields:
        vals = [to_number(r.get(f, "")) for r in rows]
        nums = [v for v in vals if v is not None]
        if not nums:
            continue
        metric_stats[f] = {
            "count": len(nums),
            "min": round(min(nums), 12),
            "median": round(percentile(nums, 0.5), 12),
            "p95": round(percentile(nums, 0.95), 12),
        }

    baseline = {
        "baseline_id": baseline_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "block": args.block,
        "summary_csv": summary_csv.as_posix(),
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "compare": {
            "official_status_fields": official_fields,
            "status_fields": detected_status,
            "profile_key_fields": ["dataset_id", "combo_id", "case_id", "case_seed"],
        },
        "profiles": profiles,
        "expected_rows": status_rows,
        "pass_rates": pass_rates(rows, detected_status),
        "metric_stats": metric_stats,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"baseline_json: {out_json.as_posix()}")
    print(f"profiles:      {len(profiles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
