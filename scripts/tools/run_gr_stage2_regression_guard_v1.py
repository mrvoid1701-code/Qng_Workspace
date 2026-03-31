#!/usr/bin/env python3
"""Stage-2 regression guard against frozen Stage-2 baseline summary."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BASELINE = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-regression-baseline-v1"
    / "gr_stage2_baseline_official.json"
)
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v4"
    / "summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-regression-baseline-v1"
    / "latest_check"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Stage-2 regression guard against frozen baseline.")
    p.add_argument("--baseline-json", default=str(DEFAULT_BASELINE))
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def main() -> int:
    args = parse_args()
    baseline_path = Path(args.baseline_json).resolve()
    summary_path = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not baseline_path.exists():
        raise FileNotFoundError(f"baseline not found: {baseline_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"summary not found: {summary_path}")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    expected_rows = list(baseline.get("expected_rows", []))
    status_fields = list((baseline.get("compare", {}) or {}).get("status_fields", []))
    if not status_fields:
        raise RuntimeError("baseline compare.status_fields missing")

    observed_rows = read_csv(summary_path)
    obs_map: dict[str, dict[str, str]] = {}
    for r in observed_rows:
        try:
            k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
        except Exception:
            continue
        obs_map[k] = r

    summary_out_rows: list[dict[str, Any]] = []
    mismatch_rows: list[dict[str, Any]] = []
    missing_profiles = 0
    mismatch_profiles = 0

    for exp in expected_rows:
        ds = str(exp.get("dataset_id", ""))
        seed = int(exp.get("seed", 0))
        k = key_of(ds, seed)
        obs = obs_map.get(k)
        if obs is None:
            missing_profiles += 1
            summary_out_rows.append(
                {
                    "dataset_id": ds,
                    "seed": seed,
                    "status": "missing",
                    "mismatch_count": len(status_fields),
                    "fields_checked": len(status_fields),
                }
            )
            continue

        mm_count = 0
        for field in status_fields:
            ev = norm_status(str(exp.get(field, "")))
            ov = norm_status(str(obs.get(field, "")))
            if ev != ov:
                mm_count += 1
                mismatch_rows.append(
                    {
                        "dataset_id": ds,
                        "seed": seed,
                        "field": field,
                        "expected": ev,
                        "observed": ov,
                    }
                )
        if mm_count > 0:
            mismatch_profiles += 1

        summary_out_rows.append(
            {
                "dataset_id": ds,
                "seed": seed,
                "status": "pass" if mm_count == 0 else "mismatch",
                "mismatch_count": mm_count,
                "fields_checked": len(status_fields),
            }
        )

    expected_keys = {key_of(str(r.get("dataset_id", "")), int(r.get("seed", 0))) for r in expected_rows}
    extra_profiles = sum(1 for k in obs_map.keys() if k not in expected_keys)
    total = len(expected_rows)
    pass_profiles = sum(1 for r in summary_out_rows if r["status"] == "pass")
    guard_pass = (missing_profiles == 0 and mismatch_profiles == 0)

    write_csv(
        out_dir / "observed_summary.csv",
        summary_out_rows,
        ["dataset_id", "seed", "status", "mismatch_count", "fields_checked"],
    )
    write_csv(
        out_dir / "mismatches.csv",
        mismatch_rows,
        ["dataset_id", "seed", "field", "expected", "observed"],
    )

    report = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "baseline_json": baseline_path.as_posix(),
        "summary_csv": summary_path.as_posix(),
        "baseline_id": baseline.get("baseline_id", ""),
        "effective_tag": baseline.get("effective_tag", ""),
        "profiles_total": total,
        "profiles_pass": pass_profiles,
        "profiles_missing": missing_profiles,
        "profiles_mismatch": mismatch_profiles,
        "profiles_extra": extra_profiles,
        "status_fields": status_fields,
        "decision": "PASS" if guard_pass else "FAIL",
    }
    (out_dir / "regression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# GR Stage-2 Regression Guard Report (v1)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- baseline_id: `{report['baseline_id']}`",
        f"- effective_tag: `{report['effective_tag']}`",
        f"- decision: `{report['decision']}`",
        "",
        "## Summary",
        "",
        f"- profiles_total: `{total}`",
        f"- profiles_pass: `{pass_profiles}`",
        f"- profiles_missing: `{missing_profiles}`",
        f"- profiles_mismatch: `{mismatch_profiles}`",
        f"- profiles_extra: `{extra_profiles}`",
        "",
        "## Compared Status Fields",
        "",
        ", ".join(f"`{f}`" for f in status_fields),
        "",
    ]
    (out_dir / "regression_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"observed_summary: {out_dir / 'observed_summary.csv'}")
    print(f"mismatches_csv:   {out_dir / 'mismatches.csv'}")
    print(f"report_md:        {out_dir / 'regression_report.md'}")
    print(f"report_json:      {out_dir / 'regression_report.json'}")

    if args.strict_exit and not guard_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
