#!/usr/bin/env python3
"""Build stability convergence v6 regression baseline JSON."""

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
AUDIT = BASE / "stability-convergence-v6-audit-v1"
BASELINE_DIR = BASE / "stability-convergence-v6-regression-baseline-v1"

BLOCK_DEFAULTS = {
    "primary": {
        "seed_checks_csv": AUDIT / "primary_s3401_3420" / "v6_candidate" / "seed_checks.csv",
        "report_json": AUDIT / "primary_s3401_3420" / "v6_candidate" / "report.json",
        "out_json": BASELINE_DIR / "stability_convergence_v6_baseline_primary.json",
        "baseline_id": "stability-convergence-v6-baseline-primary-v1",
    },
    "attack": {
        "seed_checks_csv": AUDIT / "attack_seed3601_3620" / "v6_candidate" / "seed_checks.csv",
        "report_json": AUDIT / "attack_seed3601_3620" / "v6_candidate" / "report.json",
        "out_json": BASELINE_DIR / "stability_convergence_v6_baseline_attack.json",
        "baseline_id": "stability-convergence-v6-baseline-attack-v1",
    },
    "holdout": {
        "seed_checks_csv": AUDIT / "holdout_regime_shift_s3501_3520" / "v6_candidate" / "seed_checks.csv",
        "report_json": AUDIT / "holdout_regime_shift_s3501_3520" / "v6_candidate" / "report.json",
        "out_json": BASELINE_DIR / "stability_convergence_v6_baseline_holdout.json",
        "baseline_id": "stability-convergence-v6-baseline-holdout-v1",
    },
}

STATUS_FIELDS = [
    "structural_seed_pass",
    "bulk_valid",
    "full_slope_negative",
    "bulk_slope_negative",
    "all_pass_convergence_v6_seed",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build stability convergence v6 baseline JSON.")
    p.add_argument("--block", choices=("primary", "attack", "holdout"), required=True)
    p.add_argument("--seed-checks-csv", default="")
    p.add_argument("--report-json", default="")
    p.add_argument("--out-json", default="")
    p.add_argument("--baseline-id", default="")
    p.add_argument("--effective-tag", default="stability-convergence-v6-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument("--telemetry-full-margin", type=float, default=0.05)
    p.add_argument("--telemetry-bulk-margin", type=float, default=0.05)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def norm_bool(v: Any) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes", "pass"}


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        x = float(str(v).strip())
    except Exception:
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return x


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
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


def pass_rates(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, dict[str, Any]]:
    n = len(rows)
    out: dict[str, dict[str, Any]] = {}
    for f in fields:
        p = sum(1 for r in rows if norm_bool(r.get(f, "")))
        out[f] = {"pass": p, "total": n, "pass_rate": (p / n if n else 0.0)}
    return out


def main() -> int:
    args = parse_args()
    defaults = BLOCK_DEFAULTS[args.block]
    seed_checks_csv = Path(args.seed_checks_csv).resolve() if args.seed_checks_csv else Path(defaults["seed_checks_csv"]).resolve()
    report_json = Path(args.report_json).resolve() if args.report_json else Path(defaults["report_json"]).resolve()
    out_json = Path(args.out_json).resolve() if args.out_json else Path(defaults["out_json"]).resolve()
    baseline_id = args.baseline_id.strip() or str(defaults["baseline_id"])

    if not seed_checks_csv.exists():
        raise FileNotFoundError(f"seed checks missing: {seed_checks_csv}")
    if not report_json.exists():
        raise FileNotFoundError(f"report missing: {report_json}")

    seed_rows = read_csv(seed_checks_csv)
    if not seed_rows:
        raise RuntimeError("seed checks csv has zero rows")
    report = json.loads(report_json.read_text(encoding="utf-8"))

    expected_rows: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    full_slopes: list[float] = []
    bulk_slopes: list[float] = []
    full_positive = 0
    bulk_positive = 0

    for r in sorted(seed_rows, key=lambda rr: int(str(rr.get("seed", "0"))) if str(rr.get("seed", "")).isdigit() else str(rr.get("seed", ""))):
        seed = str(r.get("seed", "")).strip()
        structural = norm_bool(r.get("structural_seed_pass", ""))
        bulk_valid = norm_bool(r.get("bulk_valid", ""))
        full_slope = to_float(r.get("full_slope_theilsen", ""), 0.0)
        bulk_slope = to_float(r.get("bulk_slope_theilsen", ""), 0.0)
        full_neg = full_slope < 0.0
        bulk_neg = bulk_slope < 0.0
        all_pass = structural and bulk_valid and full_neg and bulk_neg

        full_slopes.append(full_slope)
        bulk_slopes.append(bulk_slope)
        if full_slope >= 0.0:
            full_positive += 1
        if bulk_slope >= 0.0:
            bulk_positive += 1

        profiles.append({"seed": seed})
        expected_rows.append(
            {
                "seed": seed,
                "structural_seed_pass": "true" if structural else "false",
                "bulk_valid": "true" if bulk_valid else "false",
                "full_slope_negative": "true" if full_neg else "false",
                "bulk_slope_negative": "true" if bulk_neg else "false",
                "all_pass_convergence_v6_seed": "true" if all_pass else "false",
            }
        )

    n = len(expected_rows)
    full_positive_fraction = full_positive / n
    bulk_positive_fraction = bulk_positive / n
    telemetry = {
        "full_positive_seed_fraction_baseline": round(full_positive_fraction, 6),
        "bulk_positive_seed_fraction_baseline": round(bulk_positive_fraction, 6),
        "full_positive_seed_fraction_alarm_threshold": round(clamp01(full_positive_fraction + args.telemetry_full_margin), 6),
        "bulk_positive_seed_fraction_alarm_threshold": round(clamp01(bulk_positive_fraction + args.telemetry_bulk_margin), 6),
        "alarm_policy": "non_blocking",
    }

    baseline = {
        "baseline_id": baseline_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "block": args.block,
        "seed_checks_csv": seed_checks_csv.as_posix(),
        "report_json": report_json.as_posix(),
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "compare": {
            "official_status_fields": STATUS_FIELDS,
            "status_fields": STATUS_FIELDS,
            "profile_key_fields": ["seed"],
        },
        "profiles": profiles,
        "expected_rows": expected_rows,
        "pass_rates": pass_rates(expected_rows, STATUS_FIELDS),
        "metric_stats": {
            "full_slope_theilsen": {
                "count": len(full_slopes),
                "min": round(min(full_slopes), 12),
                "median": round(median(full_slopes), 12),
                "p95": round(percentile(full_slopes, 0.95), 12),
            },
            "bulk_slope_theilsen": {
                "count": len(bulk_slopes),
                "min": round(min(bulk_slopes), 12),
                "median": round(median(bulk_slopes), 12),
                "p95": round(percentile(bulk_slopes, 0.95), 12),
            },
        },
        "decision_expected": str(report.get("decision", "FAIL")),
        "report_checks_expected": {
            "s2_all_seeds_pass_ok": bool((report.get("checks", {}) or {}).get("s2_all_seeds_pass_ok", False)),
            "bulk_valid_all_seeds_ok": bool((report.get("checks", {}) or {}).get("bulk_valid_all_seeds_ok", False)),
            "s1_full_slope_ci_excludes_zero_neg_ok": bool((report.get("checks", {}) or {}).get("s1_full_slope_ci_excludes_zero_neg_ok", False)),
            "s1_bulk_slope_ci_excludes_zero_neg_ok": bool((report.get("checks", {}) or {}).get("s1_bulk_slope_ci_excludes_zero_neg_ok", False)),
        },
        "telemetry": telemetry,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"baseline_json: {out_json.as_posix()}")
    print(f"profiles:      {len(profiles)}")
    print(f"decision:      {baseline['decision_expected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
