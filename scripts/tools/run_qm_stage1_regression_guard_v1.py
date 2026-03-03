#!/usr/bin/env python3
"""QM Stage-1 regression guard against frozen primary/attack/holdout baselines."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "05_validation" / "evidence" / "artifacts"
BASELINE_DIR = BASE / "qm-stage1-regression-baseline-v1"
OFFICIAL_DIR = BASE / "qm-stage1-official-v2"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QM Stage-1 regression guard (v1).")
    p.add_argument(
        "--baseline-primary-json",
        default=str(BASELINE_DIR / "qm_stage1_baseline_primary.json"),
    )
    p.add_argument(
        "--baseline-attack-json",
        default=str(BASELINE_DIR / "qm_stage1_baseline_attack.json"),
    )
    p.add_argument(
        "--baseline-holdout-json",
        default=str(BASELINE_DIR / "qm_stage1_baseline_holdout.json"),
    )
    p.add_argument(
        "--summary-primary-csv",
        default=str(OFFICIAL_DIR / "primary_ds002_003_006_s3401_3600" / "summary.csv"),
    )
    p.add_argument(
        "--summary-attack-csv",
        default=str(OFFICIAL_DIR / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv"),
    )
    p.add_argument(
        "--summary-holdout-csv",
        default=str(OFFICIAL_DIR / "attack_holdout_ds004_008_s3401_3600" / "summary.csv"),
    )
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


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


def split_key(key: str) -> tuple[str, int]:
    ds, seed = key.split("::", 1)
    return ds, int(seed)


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def pass_rate(rows: list[dict[str, Any]], field: str) -> tuple[int, int, float]:
    n = len(rows)
    pass_count = sum(1 for r in rows if norm_status(str(r.get(field, ""))) == "pass")
    rate = (pass_count / n) if n else 0.0
    return pass_count, n, rate


def baseline_rate_for_field(baseline: dict[str, Any], field: str) -> float:
    official = ((baseline.get("pass_rates", {}) or {}).get("official", {}) or {}).get(field)
    if isinstance(official, dict) and "pass_rate" in official:
        try:
            return float(official["pass_rate"])
        except Exception:
            pass
    all_status = ((baseline.get("pass_rates", {}) or {}).get("all_status_fields", {}) or {}).get(field)
    if isinstance(all_status, dict) and "pass_rate" in all_status:
        try:
            return float(all_status["pass_rate"])
        except Exception:
            pass
    exp_rows = list(baseline.get("expected_rows", []))
    _, _, pr = pass_rate(exp_rows, field)
    return pr


def load_baseline(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"baseline missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    block_specs = [
        ("primary", Path(args.baseline_primary_json).resolve(), Path(args.summary_primary_csv).resolve()),
        ("attack", Path(args.baseline_attack_json).resolve(), Path(args.summary_attack_csv).resolve()),
        ("holdout", Path(args.baseline_holdout_json).resolve(), Path(args.summary_holdout_csv).resolve()),
    ]

    pass_rate_rows: list[dict[str, Any]] = []
    profile_diff_rows: list[dict[str, Any]] = []
    status_mismatch_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    overall_fail_reasons: list[str] = []

    for block_id, baseline_path, summary_path in block_specs:
        baseline = load_baseline(baseline_path)
        if not summary_path.exists():
            raise FileNotFoundError(f"summary missing for block={block_id}: {summary_path}")

        baseline_profiles = list(baseline.get("profiles", []))
        expected_rows = list(baseline.get("expected_rows", []))
        official_fields = list((baseline.get("compare", {}) or {}).get("official_status_fields", []))
        status_fields = list((baseline.get("compare", {}) or {}).get("status_fields", []))
        if not official_fields:
            raise RuntimeError(f"baseline missing compare.official_status_fields: {baseline_path}")
        if not baseline_profiles and not expected_rows:
            raise RuntimeError(f"baseline missing profiles: {baseline_path}")

        observed_rows = read_csv(summary_path)

        exp_keys: set[str] = set()
        for r in baseline_profiles:
            try:
                exp_keys.add(key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0")))))
            except Exception:
                continue
        if not exp_keys:
            for r in expected_rows:
                try:
                    exp_keys.add(key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0")))))
                except Exception:
                    continue

        exp_map: dict[str, dict[str, Any]] = {}
        for r in expected_rows:
            try:
                k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
            except Exception:
                continue
            exp_map[k] = r

        obs_map: dict[str, dict[str, str]] = {}
        for r in observed_rows:
            try:
                k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
            except Exception:
                continue
            obs_map[k] = r

        obs_keys = set(obs_map.keys())
        missing_keys = sorted(exp_keys - obs_keys)
        extra_keys = sorted(obs_keys - exp_keys)
        common_keys = sorted(exp_keys & obs_keys)

        for k in missing_keys:
            ds, seed = split_key(k)
            profile_diff_rows.append(
                {"block_id": block_id, "dataset_id": ds, "seed": seed, "diff_type": "missing"}
            )
        for k in extra_keys:
            ds, seed = split_key(k)
            profile_diff_rows.append({"block_id": block_id, "dataset_id": ds, "seed": seed, "diff_type": "extra"})

        if exp_map and status_fields:
            for k in common_keys:
                ds, seed = split_key(k)
                exp = exp_map[k]
                obs = obs_map[k]
                for field in status_fields:
                    ev = norm_status(str(exp.get(field, "")))
                    ov = norm_status(str(obs.get(field, "")))
                    if ev != ov:
                        status_mismatch_rows.append(
                            {
                                "block_id": block_id,
                                "dataset_id": ds,
                                "seed": seed,
                                "field": field,
                                "expected": ev,
                                "observed": ov,
                            }
                        )

        observed_for_rate: list[dict[str, str]] = []
        for k in exp_keys:
            if k in obs_map:
                observed_for_rate.append(obs_map[k])
            else:
                ds, seed = split_key(k)
                observed_for_rate.append({"dataset_id": ds, "seed": str(seed)})

        degraded_fields = 0
        for field in official_fields:
            bpr = baseline_rate_for_field(baseline, field)
            _, _, opr = pass_rate(observed_for_rate, field)
            degraded = opr + 1e-12 < bpr
            if degraded:
                degraded_fields += 1
            pass_rate_rows.append(
                {
                    "block_id": block_id,
                    "field": field,
                    "baseline_pass_rate": round(bpr, 6),
                    "observed_pass_rate": round(opr, 6),
                    "delta_pp": round((opr - bpr) * 100.0, 6),
                    "degraded": "true" if degraded else "false",
                }
            )

        mismatch_rows_block = sum(1 for r in status_mismatch_rows if r["block_id"] == block_id)
        block_pass = (len(missing_keys) == 0 and len(extra_keys) == 0 and degraded_fields == 0)
        if not block_pass:
            if missing_keys or extra_keys:
                overall_fail_reasons.append(f"{block_id}:profile_set_mismatch")
            if degraded_fields > 0:
                overall_fail_reasons.append(f"{block_id}:official_pass_rate_degraded")

        block_rows.append(
            {
                "block_id": block_id,
                "baseline_json": baseline_path.as_posix(),
                "summary_csv": summary_path.as_posix(),
                "profiles_expected": len(exp_keys),
                "profiles_observed": len(obs_keys),
                "profiles_missing": len(missing_keys),
                "profiles_extra": len(extra_keys),
                "official_fields_checked": len(official_fields),
                "official_fields_degraded": degraded_fields,
                "status_mismatches": mismatch_rows_block,
                "decision": "PASS" if block_pass else "FAIL",
            }
        )

    overall_pass = all(r["decision"] == "PASS" for r in block_rows)
    decision = "PASS" if overall_pass else "FAIL"

    write_csv(
        out_dir / "pass_rate_checks.csv",
        pass_rate_rows,
        ["block_id", "field", "baseline_pass_rate", "observed_pass_rate", "delta_pp", "degraded"],
    )
    write_csv(
        out_dir / "profile_diffs.csv",
        profile_diff_rows,
        ["block_id", "dataset_id", "seed", "diff_type"],
    )
    write_csv(
        out_dir / "status_mismatches.csv",
        status_mismatch_rows,
        ["block_id", "dataset_id", "seed", "field", "expected", "observed"],
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
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "decision": decision,
        "blocks": block_rows,
        "fail_reasons": sorted(set(overall_fail_reasons)),
        "artifacts": {
            "pass_rate_checks_csv": (out_dir / "pass_rate_checks.csv").as_posix(),
            "profile_diffs_csv": (out_dir / "profile_diffs.csv").as_posix(),
            "status_mismatches_csv": (out_dir / "status_mismatches.csv").as_posix(),
            "block_summary_csv": (out_dir / "block_summary.csv").as_posix(),
        },
    }
    (out_dir / "regression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QM Stage-1 Regression Guard Report (v1)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- decision: `{decision}`",
        "",
        "## Block Summary",
        "",
    ]
    for row in block_rows:
        lines.extend(
            [
                f"### {row['block_id']}",
                f"- decision: `{row['decision']}`",
                f"- profiles_expected/observed: `{row['profiles_expected']}/{row['profiles_observed']}`",
                f"- profiles_missing: `{row['profiles_missing']}`",
                f"- profiles_extra: `{row['profiles_extra']}`",
                f"- official_fields_degraded: `{row['official_fields_degraded']}`",
                f"- status_mismatches: `{row['status_mismatches']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Failure Criteria",
            "",
            "- FAIL if any expected `(dataset_id, seed)` profile is missing.",
            "- FAIL if any extra `(dataset_id, seed)` profile appears.",
            "- FAIL if any official gate pass rate decreases vs baseline.",
            "",
        ]
    )
    if overall_fail_reasons:
        lines.append("## Fail Reasons")
        lines.append("")
        for reason in sorted(set(overall_fail_reasons)):
            lines.append(f"- `{reason}`")
        lines.append("")

    (out_dir / "regression_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"pass_rate_checks: {out_dir / 'pass_rate_checks.csv'}")
    print(f"profile_diffs:     {out_dir / 'profile_diffs.csv'}")
    print(f"status_mismatches: {out_dir / 'status_mismatches.csv'}")
    print(f"block_summary:     {out_dir / 'block_summary.csv'}")
    print(f"report_md:         {out_dir / 'regression_report.md'}")
    print(f"report_json:       {out_dir / 'regression_report.json'}")

    if args.strict_exit and not overall_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
