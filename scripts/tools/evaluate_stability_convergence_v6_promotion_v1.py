#!/usr/bin/env python3
"""
Evaluate stability convergence v6 promotion readiness against legacy (v5-like) gate.

Checks:
- degraded=0 at seed level (legacy pass -> v6 fail)
- v6 block decision PASS on primary/attack/holdout
- holdout block PASS under shifted regime
- anti "win-by-definition" diagnostics: slope-sign consistency across seeds
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_AUDIT_ROOT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v6-audit-v1"
DEFAULT_OUT_DIR = DEFAULT_AUDIT_ROOT
DEFAULT_BLOCKS = "primary_s3401_3420,attack_seed3601_3620,holdout_regime_shift_s3501_3520"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate stability convergence v6 promotion readiness.")
    p.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT))
    p.add_argument("--blocks", default=DEFAULT_BLOCKS)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--eval-id", default="stability-convergence-v6-promotion-eval-v1")
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-all-v6-pass", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-holdout-pass", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(str(v).strip())
    except Exception:
        return default


def is_true(v: Any) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes", "pass"}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def evaluate_block(audit_root: Path, block_id: str) -> dict[str, Any]:
    legacy_dir = audit_root / block_id / "legacy_v5like"
    v6_dir = audit_root / block_id / "v6_candidate"
    legacy_report = read_json(legacy_dir / "report.json")
    v6_report = read_json(v6_dir / "report.json")
    legacy_seed_rows = read_csv(legacy_dir / "seed_checks.csv")
    v6_seed_rows = read_csv(v6_dir / "seed_checks.csv")

    legacy_by_seed = {str(r.get("seed", "")).strip(): r for r in legacy_seed_rows}
    v6_by_seed = {str(r.get("seed", "")).strip(): r for r in v6_seed_rows}
    common_seeds = sorted(set(legacy_by_seed.keys()) & set(v6_by_seed.keys()), key=lambda s: int(s) if s.isdigit() else s)

    degraded_seed = 0
    improved_seed = 0
    legacy_seed_pass = 0
    v6_seed_pass = 0
    full_slopes: list[float] = []
    bulk_slopes: list[float] = []
    full_pos = 0
    bulk_pos = 0
    missing_seed_count = len(set(legacy_by_seed.keys()) ^ set(v6_by_seed.keys()))

    for seed in common_seeds:
        lr = legacy_by_seed[seed]
        vr = v6_by_seed[seed]
        legacy_pass = is_true(lr.get("full_pass", "")) and is_true(lr.get("bulk_pass", "")) and is_true(lr.get("bulk_support_ok", ""))
        full_slope = to_float(vr.get("full_slope_theilsen", ""), 0.0)
        bulk_slope = to_float(vr.get("bulk_slope_theilsen", ""), 0.0)
        v6_pass = is_true(vr.get("structural_seed_pass", "")) and is_true(vr.get("bulk_valid", "")) and (full_slope < 0.0) and (bulk_slope < 0.0)

        full_slopes.append(full_slope)
        bulk_slopes.append(bulk_slope)
        if full_slope >= 0.0:
            full_pos += 1
        if bulk_slope >= 0.0:
            bulk_pos += 1

        if legacy_pass:
            legacy_seed_pass += 1
        if v6_pass:
            v6_seed_pass += 1
        if legacy_pass and not v6_pass:
            degraded_seed += 1
        if (not legacy_pass) and v6_pass:
            improved_seed += 1

    legacy_decision = str(legacy_report.get("decision", "FAIL"))
    v6_decision = str(v6_report.get("decision", "FAIL"))
    decision_degraded = (legacy_decision == "PASS" and v6_decision != "PASS")

    checks = v6_report.get("checks", {}) or {}
    s2_ok = bool(checks.get("s2_all_seeds_pass_ok", False)) and bool(checks.get("bulk_valid_all_seeds_ok", False))
    s1_ok = bool(checks.get("s1_full_slope_ci_excludes_zero_neg_ok", False)) and bool(checks.get("s1_bulk_slope_ci_excludes_zero_neg_ok", False))

    return {
        "block_id": block_id,
        "seed_count_common": len(common_seeds),
        "missing_seed_count": missing_seed_count,
        "legacy_decision": legacy_decision,
        "v6_decision": v6_decision,
        "decision_degraded": decision_degraded,
        "legacy_seed_pass_count": legacy_seed_pass,
        "v6_seed_pass_count": v6_seed_pass,
        "improved_seed_count": improved_seed,
        "degraded_seed_count": degraded_seed,
        "s2_all_ok": s2_ok,
        "s1_ci_ok": s1_ok,
        "v6_full_slope_median": median(full_slopes),
        "v6_bulk_slope_median": median(bulk_slopes),
        "v6_full_slope_positive_seed_count": full_pos,
        "v6_bulk_slope_positive_seed_count": bulk_pos,
        "v6_full_slope_ci_high": to_float(checks.get("full_slope_ci_high", 0.0), 0.0),
        "v6_bulk_slope_ci_high": to_float(checks.get("bulk_slope_ci_high", 0.0), 0.0),
        "legacy_report_json": (legacy_dir / "report.json").as_posix(),
        "v6_report_json": (v6_dir / "report.json").as_posix(),
    }


def main() -> int:
    args = parse_args()
    audit_root = Path(args.audit_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    block_ids = [x.strip() for x in str(args.blocks).split(",") if x.strip()]
    if not block_ids:
        raise RuntimeError("no blocks provided")

    block_rows = [evaluate_block(audit_root, bid) for bid in block_ids]
    for r in block_rows:
        for key in ["decision_degraded", "s2_all_ok", "s1_ci_ok"]:
            r[key] = "true" if bool(r[key]) else "false"

    summary_csv = out_dir / "block_summary.csv"
    write_csv(
        summary_csv,
        block_rows,
        [
            "block_id",
            "seed_count_common",
            "missing_seed_count",
            "legacy_decision",
            "v6_decision",
            "decision_degraded",
            "legacy_seed_pass_count",
            "v6_seed_pass_count",
            "improved_seed_count",
            "degraded_seed_count",
            "s2_all_ok",
            "s1_ci_ok",
            "v6_full_slope_median",
            "v6_bulk_slope_median",
            "v6_full_slope_positive_seed_count",
            "v6_bulk_slope_positive_seed_count",
            "v6_full_slope_ci_high",
            "v6_bulk_slope_ci_high",
            "legacy_report_json",
            "v6_report_json",
        ],
    )

    total_degraded_seed = sum(int(r["degraded_seed_count"]) for r in block_rows)
    total_missing = sum(int(r["missing_seed_count"]) for r in block_rows)
    any_v6_fail = any(str(r["v6_decision"]) != "PASS" for r in block_rows)
    any_decision_degraded = any(str(r["decision_degraded"]) == "true" for r in block_rows)
    any_s2_fail = any(str(r["s2_all_ok"]) != "true" for r in block_rows)
    any_s1_fail = any(str(r["s1_ci_ok"]) != "true" for r in block_rows)
    any_positive_seed_slope = any(
        int(r["v6_full_slope_positive_seed_count"]) > 0 or int(r["v6_bulk_slope_positive_seed_count"]) > 0 for r in block_rows
    )

    holdout_row = next((r for r in block_rows if "holdout" in str(r.get("block_id", "")).lower()), None)
    holdout_pass = bool(holdout_row and str(holdout_row.get("v6_decision", "")) == "PASS")

    checks = {
        "zero_degraded_seed": (total_degraded_seed == 0 and not any_decision_degraded),
        "all_v6_blocks_pass": (not any_v6_fail),
        "holdout_shift_block_pass": holdout_pass,
        "no_seed_set_mismatch": (total_missing == 0),
        "s2_all_blocks_ok": (not any_s2_fail),
        "s1_ci_all_blocks_ok": (not any_s1_fail),
        "no_positive_seed_slopes": (not any_positive_seed_slope),
    }

    decision = "PASS"
    if args.require_zero_degraded and not checks["zero_degraded_seed"]:
        decision = "FAIL"
    if args.require_all_v6_pass and not checks["all_v6_blocks_pass"]:
        decision = "FAIL"
    if args.require_holdout_pass and not checks["holdout_shift_block_pass"]:
        decision = "FAIL"
    if not checks["no_seed_set_mismatch"] or not checks["s2_all_blocks_ok"] or not checks["s1_ci_all_blocks_ok"]:
        decision = "FAIL"

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "audit_root": audit_root.as_posix(),
        "blocks": block_ids,
        "checks": checks,
        "totals": {
            "block_count": len(block_rows),
            "total_degraded_seed_count": total_degraded_seed,
            "total_missing_seed_count": total_missing,
        },
        "decision": decision,
    }
    report_json = out_dir / "promotion_report.json"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence v6 Promotion Eval v1",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- audit_root: `{audit_root.as_posix()}`",
        f"- decision: `{decision}`",
        "",
        "## Guard Checks",
        "",
        f"- zero_degraded_seed: `{'true' if checks['zero_degraded_seed'] else 'false'}`",
        f"- all_v6_blocks_pass: `{'true' if checks['all_v6_blocks_pass'] else 'false'}`",
        f"- holdout_shift_block_pass: `{'true' if checks['holdout_shift_block_pass'] else 'false'}`",
        f"- no_seed_set_mismatch: `{'true' if checks['no_seed_set_mismatch'] else 'false'}`",
        f"- s2_all_blocks_ok: `{'true' if checks['s2_all_blocks_ok'] else 'false'}`",
        f"- s1_ci_all_blocks_ok: `{'true' if checks['s1_ci_all_blocks_ok'] else 'false'}`",
        f"- no_positive_seed_slopes: `{'true' if checks['no_positive_seed_slopes'] else 'false'}`",
        "",
        "## Notes",
        "",
        "- Legacy comparator is v5-like convergence gate (run via v4 engine with frozen v5 constants).",
        "- v6 seed diagnostics use strict per-seed slope sign (`full<0`, `bulk<0`) plus structural/bulk-valid flags.",
        "- `no_positive_seed_slopes` is an anti-masking check (guards against median-only wins hiding positive-slope seeds).",
    ]
    report_md = out_dir / "promotion_report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"block_summary_csv: {summary_csv.as_posix()}")
    print(f"report_md:         {report_md.as_posix()}")
    print(f"report_json:       {report_json.as_posix()}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
