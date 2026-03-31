#!/usr/bin/env python3
"""Stability convergence v6 regression guard against frozen baselines."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "05_validation" / "evidence" / "artifacts"
BASELINE_DIR = BASE / "stability-convergence-v6-regression-baseline-v1"
AUDIT_DIR = BASE / "stability-convergence-v6-audit-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence v6 regression guard.")
    p.add_argument("--baseline-primary-json", default=str(BASELINE_DIR / "stability_convergence_v6_baseline_primary.json"))
    p.add_argument("--baseline-attack-json", default=str(BASELINE_DIR / "stability_convergence_v6_baseline_attack.json"))
    p.add_argument("--baseline-holdout-json", default=str(BASELINE_DIR / "stability_convergence_v6_baseline_holdout.json"))
    p.add_argument("--seed-checks-primary-csv", default=str(AUDIT_DIR / "primary_s3401_3420" / "v6_candidate" / "seed_checks.csv"))
    p.add_argument("--seed-checks-attack-csv", default=str(AUDIT_DIR / "attack_seed3601_3620" / "v6_candidate" / "seed_checks.csv"))
    p.add_argument("--seed-checks-holdout-csv", default=str(AUDIT_DIR / "holdout_regime_shift_s3501_3520" / "v6_candidate" / "seed_checks.csv"))
    p.add_argument("--report-primary-json", default=str(AUDIT_DIR / "primary_s3401_3420" / "v6_candidate" / "report.json"))
    p.add_argument("--report-attack-json", default=str(AUDIT_DIR / "attack_seed3601_3620" / "v6_candidate" / "report.json"))
    p.add_argument("--report-holdout-json", default=str(AUDIT_DIR / "holdout_regime_shift_s3501_3520" / "v6_candidate" / "report.json"))
    p.add_argument("--out-dir", default=str(BASELINE_DIR / "latest_check"))
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
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


def norm_bool(v: Any) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes", "pass"}


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(str(v).strip())
    except Exception:
        return default


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing json: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def pass_rate(rows: list[dict[str, Any]], field: str) -> tuple[int, int, float]:
    n = len(rows)
    p = sum(1 for r in rows if norm_bool(r.get(field, "")))
    return p, n, (p / n if n else 0.0)


def key_of_seed(row: dict[str, Any]) -> str:
    return str(row.get("seed", "")).strip()


def derive_status_row(seed_row: dict[str, str]) -> dict[str, Any]:
    seed = str(seed_row.get("seed", "")).strip()
    structural = norm_bool(seed_row.get("structural_seed_pass", ""))
    bulk_valid = norm_bool(seed_row.get("bulk_valid", ""))
    full_slope = to_float(seed_row.get("full_slope_theilsen", ""), 0.0)
    bulk_slope = to_float(seed_row.get("bulk_slope_theilsen", ""), 0.0)
    full_neg = full_slope < 0.0
    bulk_neg = bulk_slope < 0.0
    return {
        "seed": seed,
        "structural_seed_pass": "true" if structural else "false",
        "bulk_valid": "true" if bulk_valid else "false",
        "full_slope_negative": "true" if full_neg else "false",
        "bulk_slope_negative": "true" if bulk_neg else "false",
        "all_pass_convergence_v6_seed": "true" if (structural and bulk_valid and full_neg and bulk_neg) else "false",
        "full_slope_theilsen": full_slope,
        "bulk_slope_theilsen": bulk_slope,
    }


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = [
        (
            "primary",
            Path(args.baseline_primary_json).resolve(),
            Path(args.seed_checks_primary_csv).resolve(),
            Path(args.report_primary_json).resolve(),
        ),
        (
            "attack",
            Path(args.baseline_attack_json).resolve(),
            Path(args.seed_checks_attack_csv).resolve(),
            Path(args.report_attack_json).resolve(),
        ),
        (
            "holdout",
            Path(args.baseline_holdout_json).resolve(),
            Path(args.seed_checks_holdout_csv).resolve(),
            Path(args.report_holdout_json).resolve(),
        ),
    ]

    pass_rate_rows: list[dict[str, Any]] = []
    profile_diff_rows: list[dict[str, Any]] = []
    status_mismatch_rows: list[dict[str, Any]] = []
    telemetry_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    fail_reasons: list[str] = []
    warning_reasons: list[str] = []

    for block_id, baseline_json, seed_checks_csv, report_json in blocks:
        baseline = load_json(baseline_json)
        if not seed_checks_csv.exists():
            raise FileNotFoundError(f"missing seed checks for {block_id}: {seed_checks_csv}")
        if not report_json.exists():
            raise FileNotFoundError(f"missing report for {block_id}: {report_json}")

        seed_rows = read_csv(seed_checks_csv)
        obs_rows = [derive_status_row(r) for r in seed_rows]
        report = load_json(report_json)

        official_fields = list((baseline.get("compare", {}) or {}).get("official_status_fields", []))
        status_fields = list((baseline.get("compare", {}) or {}).get("status_fields", []))
        exp_profiles = list(baseline.get("profiles", []))
        exp_rows = list(baseline.get("expected_rows", []))
        exp_map = {key_of_seed(r): r for r in exp_rows}
        obs_map = {key_of_seed(r): r for r in obs_rows}

        exp_keys = set(key_of_seed(r) for r in exp_profiles)
        obs_keys = set(obs_map.keys())
        missing = sorted(exp_keys - obs_keys)
        extra = sorted(obs_keys - exp_keys)
        common = sorted(exp_keys & obs_keys, key=lambda s: int(s) if s.isdigit() else s)

        for k in missing:
            profile_diff_rows.append({"block_id": block_id, "seed": k, "diff_type": "missing"})
        for k in extra:
            profile_diff_rows.append({"block_id": block_id, "seed": k, "diff_type": "extra"})

        mismatch_count = 0
        for k in common:
            exp = exp_map.get(k, {})
            obs = obs_map.get(k, {})
            for f in status_fields:
                ev = "true" if norm_bool(exp.get(f, "")) else "false"
                ov = "true" if norm_bool(obs.get(f, "")) else "false"
                if ev != ov:
                    mismatch_count += 1
                    status_mismatch_rows.append(
                        {"block_id": block_id, "seed": k, "field": f, "expected": ev, "observed": ov}
                    )

        exp_rows_for_rate: list[dict[str, Any]] = []
        for k in exp_keys:
            exp_rows_for_rate.append(obs_map.get(k, {"seed": k}))

        degraded_fields = 0
        for f in official_fields:
            baseline_rate = float(((baseline.get("pass_rates", {}) or {}).get(f, {}) or {}).get("pass_rate", 0.0))
            _, _, observed_rate = pass_rate(exp_rows_for_rate, f)
            degraded = observed_rate + 1e-12 < baseline_rate
            if degraded:
                degraded_fields += 1
            pass_rate_rows.append(
                {
                    "block_id": block_id,
                    "field": f,
                    "baseline_pass_rate": round(baseline_rate, 6),
                    "observed_pass_rate": round(observed_rate, 6),
                    "delta_pp": round((observed_rate - baseline_rate) * 100.0, 6),
                    "degraded": "true" if degraded else "false",
                }
            )

        decision_expected = str(baseline.get("decision_expected", "PASS")).upper()
        decision_observed = str(report.get("decision", "FAIL")).upper()
        pass_stays_pass_ok = not (decision_expected == "PASS" and decision_observed != "PASS")

        checks_observed = report.get("checks", {}) or {}
        s2_ok = bool(checks_observed.get("s2_all_seeds_pass_ok", False)) and bool(
            checks_observed.get("bulk_valid_all_seeds_ok", False)
        )
        s1_ok = bool(checks_observed.get("s1_full_slope_ci_excludes_zero_neg_ok", False)) and bool(
            checks_observed.get("s1_bulk_slope_ci_excludes_zero_neg_ok", False)
        )

        n_common = len(common) if common else 1
        pos_full = sum(1 for k in common if to_float(obs_map.get(k, {}).get("full_slope_theilsen", 0.0), 0.0) >= 0.0)
        pos_bulk = sum(1 for k in common if to_float(obs_map.get(k, {}).get("bulk_slope_theilsen", 0.0), 0.0) >= 0.0)
        pos_full_frac = pos_full / n_common
        pos_bulk_frac = pos_bulk / n_common

        telemetry_cfg = baseline.get("telemetry", {}) or {}
        alarm_thr_full = float(telemetry_cfg.get("full_positive_seed_fraction_alarm_threshold", 1.0))
        alarm_thr_bulk = float(telemetry_cfg.get("bulk_positive_seed_fraction_alarm_threshold", 1.0))
        alarm_full = pos_full_frac > alarm_thr_full + 1e-12
        alarm_bulk = pos_bulk_frac > alarm_thr_bulk + 1e-12
        if alarm_full:
            warning_reasons.append(f"{block_id}:positive_full_slope_fraction_alarm")
        if alarm_bulk:
            warning_reasons.append(f"{block_id}:positive_bulk_slope_fraction_alarm")
        telemetry_rows.append(
            {
                "block_id": block_id,
                "positive_full_slope_seed_fraction": round(pos_full_frac, 6),
                "positive_bulk_slope_seed_fraction": round(pos_bulk_frac, 6),
                "alarm_threshold_full": round(alarm_thr_full, 6),
                "alarm_threshold_bulk": round(alarm_thr_bulk, 6),
                "alarm_full": "true" if alarm_full else "false",
                "alarm_bulk": "true" if alarm_bulk else "false",
                "alarm_policy": str(telemetry_cfg.get("alarm_policy", "non_blocking")),
            }
        )

        block_pass = (len(missing) == 0 and len(extra) == 0 and degraded_fields == 0 and pass_stays_pass_ok and s2_ok and s1_ok)
        if not block_pass:
            if missing or extra:
                fail_reasons.append(f"{block_id}:profile_set_mismatch")
            if degraded_fields > 0:
                fail_reasons.append(f"{block_id}:official_pass_rate_degraded")
            if not pass_stays_pass_ok:
                fail_reasons.append(f"{block_id}:decision_regressed")
            if not s2_ok:
                fail_reasons.append(f"{block_id}:s2_check_failed")
            if not s1_ok:
                fail_reasons.append(f"{block_id}:s1_ci_check_failed")

        block_rows.append(
            {
                "block_id": block_id,
                "baseline_json": baseline_json.as_posix(),
                "seed_checks_csv": seed_checks_csv.as_posix(),
                "report_json": report_json.as_posix(),
                "seeds_expected": len(exp_keys),
                "seeds_observed": len(obs_keys),
                "seeds_missing": len(missing),
                "seeds_extra": len(extra),
                "official_fields_checked": len(official_fields),
                "official_fields_degraded": degraded_fields,
                "status_mismatches": mismatch_count,
                "decision_expected": decision_expected,
                "decision_observed": decision_observed,
                "pass_stays_pass_ok": "true" if pass_stays_pass_ok else "false",
                "s2_checks_ok": "true" if s2_ok else "false",
                "s1_ci_checks_ok": "true" if s1_ok else "false",
                "decision": "PASS" if block_pass else "FAIL",
            }
        )

    decision = "PASS" if all(r["decision"] == "PASS" for r in block_rows) else "FAIL"

    write_csv(
        out_dir / "pass_rate_checks.csv",
        pass_rate_rows,
        ["block_id", "field", "baseline_pass_rate", "observed_pass_rate", "delta_pp", "degraded"],
    )
    write_csv(
        out_dir / "profile_diffs.csv",
        profile_diff_rows,
        ["block_id", "seed", "diff_type"],
    )
    write_csv(
        out_dir / "status_mismatches.csv",
        status_mismatch_rows,
        ["block_id", "seed", "field", "expected", "observed"],
    )
    write_csv(
        out_dir / "telemetry.csv",
        telemetry_rows,
        [
            "block_id",
            "positive_full_slope_seed_fraction",
            "positive_bulk_slope_seed_fraction",
            "alarm_threshold_full",
            "alarm_threshold_bulk",
            "alarm_full",
            "alarm_bulk",
            "alarm_policy",
        ],
    )
    write_csv(
        out_dir / "block_summary.csv",
        block_rows,
        [
            "block_id",
            "baseline_json",
            "seed_checks_csv",
            "report_json",
            "seeds_expected",
            "seeds_observed",
            "seeds_missing",
            "seeds_extra",
            "official_fields_checked",
            "official_fields_degraded",
            "status_mismatches",
            "decision_expected",
            "decision_observed",
            "pass_stays_pass_ok",
            "s2_checks_ok",
            "s1_ci_checks_ok",
            "decision",
        ],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "blocks": block_rows,
        "fail_reasons": sorted(set(fail_reasons)),
        "warning_reasons": sorted(set(warning_reasons)),
        "telemetry_policy": "non_blocking_alarm",
    }
    (out_dir / "regression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence v6 Regression Guard Report (v1)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- decision: `{decision}`",
        f"- telemetry_policy: `non_blocking_alarm`",
        "",
        "## Block Summary",
        "",
    ]
    for r in block_rows:
        lines.extend(
            [
                f"### {r['block_id']}",
                f"- decision: `{r['decision']}`",
                f"- seeds_expected/observed: `{r['seeds_expected']}/{r['seeds_observed']}`",
                f"- seeds_missing: `{r['seeds_missing']}`",
                f"- seeds_extra: `{r['seeds_extra']}`",
                f"- official_fields_degraded: `{r['official_fields_degraded']}`",
                f"- pass_stays_pass_ok: `{r['pass_stays_pass_ok']}`",
                f"- s2_checks_ok: `{r['s2_checks_ok']}`",
                f"- s1_ci_checks_ok: `{r['s1_ci_checks_ok']}`",
                "",
            ]
        )
    if warning_reasons:
        lines.extend(["## Telemetry Alarms (Non-Blocking)", ""])
        for w in sorted(set(warning_reasons)):
            lines.append(f"- {w}")
        lines.append("")
    (out_dir / "regression_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"block_summary: {out_dir / 'block_summary.csv'}")
    print(f"telemetry:     {out_dir / 'telemetry.csv'}")
    print(f"report_md:     {out_dir / 'regression_report.md'}")
    print(f"report_json:   {out_dir / 'regression_report.json'}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
