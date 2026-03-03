#!/usr/bin/env python3
"""Stability regression guard against frozen official-v2 baselines."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "05_validation" / "evidence" / "artifacts"
BASELINE_DIR = BASE / "stability-regression-baseline-v1"
OFFICIAL_DIR = BASE / "stability-official-v2"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability regression guard (v1).")
    p.add_argument("--baseline-primary-json", default=str(BASELINE_DIR / "stability_baseline_primary.json"))
    p.add_argument("--baseline-attack-json", default=str(BASELINE_DIR / "stability_baseline_attack.json"))
    p.add_argument("--baseline-holdout-json", default=str(BASELINE_DIR / "stability_baseline_holdout.json"))
    p.add_argument("--summary-primary-csv", default=str(OFFICIAL_DIR / "primary_s3401" / "summary.csv"))
    p.add_argument("--summary-attack-csv", default=str(OFFICIAL_DIR / "attack_s3401_4401" / "summary.csv"))
    p.add_argument("--summary-holdout-csv", default=str(OFFICIAL_DIR / "holdout_n30_42_s3401" / "summary.csv"))
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def key_of(row: dict[str, Any]) -> str:
    return "::".join(
        [
            str(row.get("dataset_id", "")),
            str(row.get("combo_id", "")),
            str(row.get("case_id", "")),
            str(row.get("case_seed", "")),
        ]
    )


def split_key(k: str) -> tuple[str, str, str, str]:
    parts = k.split("::")
    if len(parts) != 4:
        return (k, "", "", "")
    return parts[0], parts[1], parts[2], parts[3]


def pass_rate(rows: list[dict[str, Any]], field: str) -> tuple[int, int, float]:
    n = len(rows)
    p = sum(1 for r in rows if norm_status(str(r.get(field, ""))) == "pass")
    return p, n, (p / n if n else 0.0)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing json: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = [
        ("primary", Path(args.baseline_primary_json).resolve(), Path(args.summary_primary_csv).resolve()),
        ("attack", Path(args.baseline_attack_json).resolve(), Path(args.summary_attack_csv).resolve()),
        ("holdout", Path(args.baseline_holdout_json).resolve(), Path(args.summary_holdout_csv).resolve()),
    ]

    pass_rate_rows: list[dict[str, Any]] = []
    profile_diff_rows: list[dict[str, Any]] = []
    status_mismatch_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    fail_reasons: list[str] = []

    for block_id, baseline_json, summary_csv in blocks:
        baseline = load_json(baseline_json)
        if not summary_csv.exists():
            raise FileNotFoundError(f"missing summary for {block_id}: {summary_csv}")
        obs_rows = read_csv(summary_csv)

        official_fields = list((baseline.get("compare", {}) or {}).get("official_status_fields", []))
        status_fields = list((baseline.get("compare", {}) or {}).get("status_fields", []))
        exp_profiles = list(baseline.get("profiles", []))
        exp_rows = list(baseline.get("expected_rows", []))
        exp_map = {key_of(r): r for r in exp_rows}
        obs_map = {key_of(r): r for r in obs_rows}

        exp_keys = set(key_of(r) for r in exp_profiles)
        obs_keys = set(obs_map.keys())
        missing = sorted(exp_keys - obs_keys)
        extra = sorted(obs_keys - exp_keys)
        common = sorted(exp_keys & obs_keys)

        for k in missing:
            ds, combo, case, seed = split_key(k)
            profile_diff_rows.append(
                {"block_id": block_id, "dataset_id": ds, "combo_id": combo, "case_id": case, "case_seed": seed, "diff_type": "missing"}
            )
        for k in extra:
            ds, combo, case, seed = split_key(k)
            profile_diff_rows.append(
                {"block_id": block_id, "dataset_id": ds, "combo_id": combo, "case_id": case, "case_seed": seed, "diff_type": "extra"}
            )

        mismatch_count = 0
        for k in common:
            exp = exp_map.get(k, {})
            obs = obs_map.get(k, {})
            ds, combo, case, seed = split_key(k)
            for f in status_fields:
                ev = norm_status(exp.get(f, ""))
                ov = norm_status(obs.get(f, ""))
                if ev != ov:
                    mismatch_count += 1
                    status_mismatch_rows.append(
                        {
                            "block_id": block_id,
                            "dataset_id": ds,
                            "combo_id": combo,
                            "case_id": case,
                            "case_seed": seed,
                            "field": f,
                            "expected": ev,
                            "observed": ov,
                        }
                    )

        exp_rows_for_rate: list[dict[str, Any]] = []
        for k in exp_keys:
            exp_rows_for_rate.append(obs_map.get(k, {"dataset_id": "", "combo_id": "", "case_id": "", "case_seed": ""}))

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

        block_pass = (len(missing) == 0 and len(extra) == 0 and degraded_fields == 0)
        if not block_pass:
            if missing or extra:
                fail_reasons.append(f"{block_id}:profile_set_mismatch")
            if degraded_fields > 0:
                fail_reasons.append(f"{block_id}:official_pass_rate_degraded")

        block_rows.append(
            {
                "block_id": block_id,
                "baseline_json": baseline_json.as_posix(),
                "summary_csv": summary_csv.as_posix(),
                "profiles_expected": len(exp_keys),
                "profiles_observed": len(obs_keys),
                "profiles_missing": len(missing),
                "profiles_extra": len(extra),
                "official_fields_checked": len(official_fields),
                "official_fields_degraded": degraded_fields,
                "status_mismatches": mismatch_count,
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
        ["block_id", "dataset_id", "combo_id", "case_id", "case_seed", "diff_type"],
    )
    write_csv(
        out_dir / "status_mismatches.csv",
        status_mismatch_rows,
        ["block_id", "dataset_id", "combo_id", "case_id", "case_seed", "field", "expected", "observed"],
    )
    write_csv(
        out_dir / "block_summary.csv",
        block_rows,
        [
            "block_id",
            "baseline_json",
            "summary_csv",
            "profiles_expected",
            "profiles_observed",
            "profiles_missing",
            "profiles_extra",
            "official_fields_checked",
            "official_fields_degraded",
            "status_mismatches",
            "decision",
        ],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "blocks": block_rows,
        "fail_reasons": sorted(set(fail_reasons)),
    }
    (out_dir / "regression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Regression Guard Report (v1)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- decision: `{decision}`",
        "",
        "## Block Summary",
        "",
    ]
    for r in block_rows:
        lines.extend(
            [
                f"### {r['block_id']}",
                f"- decision: `{r['decision']}`",
                f"- profiles_expected/observed: `{r['profiles_expected']}/{r['profiles_observed']}`",
                f"- profiles_missing: `{r['profiles_missing']}`",
                f"- profiles_extra: `{r['profiles_extra']}`",
                f"- official_fields_degraded: `{r['official_fields_degraded']}`",
                f"- status_mismatches: `{r['status_mismatches']}`",
                "",
            ]
        )
    (out_dir / "regression_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"block_summary: {out_dir / 'block_summary.csv'}")
    print(f"report_md:     {out_dir / 'regression_report.md'}")
    print(f"report_json:   {out_dir / 'regression_report.json'}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
