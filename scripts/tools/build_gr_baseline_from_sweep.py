#!/usr/bin/env python3
"""Build GR regression baseline JSONs from sweep summary CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

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

DEFAULT_NUMERIC_FIELDS = [
    "g15a_gamma_dev",
    "g15d_ep_ratio",
    "g15b_shapiro_ratio",
    "g15b_v2_shapiro_ratio",
    "g13b_e_cov_drift",
    "g14b_e_cov_drift",
    "g13c_speed_reduction",
]


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build GR baseline JSON from sweep summary CSV.")
    p.add_argument("--summary-csv", required=True, help="Input summary.csv from run_qng_phi_scale_sweep_v1.py")
    p.add_argument("--out-json", required=True, help="Output baseline JSON path")
    p.add_argument("--mode", choices=["survey", "official"], default="survey")
    p.add_argument("--baseline-id", default="")
    p.add_argument("--effective-tag", default="gr-ppn-g15b-v2-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument(
        "--official-status-fields",
        default=",".join(OFFICIAL_STATUS_FIELDS),
        help="Comma-separated fields used to define all_pass_official and official filtering.",
    )
    p.add_argument(
        "--numeric-fields",
        default=",".join(DEFAULT_NUMERIC_FIELDS),
        help="Comma-separated numeric fields included in baseline comparisons.",
    )
    p.add_argument("--abs-tol", type=float, default=1e-6)
    return p.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def status_is_pass(value: str) -> bool:
    return value.strip().lower() == "pass"


def derive_row_flags(row: dict[str, str], official_fields: list[str]) -> None:
    if not row.get("all_pass_diagnostic", "").strip():
        diag_ok = all(status_is_pass(row.get(field, "")) for field in DIAGNOSTIC_STATUS_FIELDS)
        row["all_pass_diagnostic"] = "pass" if diag_ok else "fail"
    if not row.get("all_pass_official", "").strip():
        off_ok = all(status_is_pass(row.get(field, "")) for field in official_fields)
        row["all_pass_official"] = "pass" if off_ok else "fail"
    if not row.get("all_pass", "").strip():
        row["all_pass"] = row["all_pass_diagnostic"]


def normalize_rows(rows: list[dict[str, str]], official_fields: list[str]) -> list[dict[str, str]]:
    norm: list[dict[str, str]] = []
    for src in rows:
        row = dict(src)
        row["dataset_id"] = row["dataset_id"].strip()
        row["seed"] = str(int(row["seed"]))
        row["phi_scale"] = f"{float(row['phi_scale']):.2f}"
        derive_row_flags(row, official_fields)
        norm.append(row)
    norm.sort(key=lambda r: (r["dataset_id"], int(r["seed"]), float(r["phi_scale"])))
    return norm


def default_baseline_id(mode: str) -> str:
    if mode == "official":
        return "gr-g10-g16-regression-official-v1"
    return "gr-g10-g16-regression-survey-grid20-v1"


def main() -> int:
    args = parse_args()
    in_csv = Path(args.summary_csv).resolve()
    out_json = Path(args.out_json).resolve()
    official_fields = parse_csv_list(args.official_status_fields)
    numeric_fields = parse_csv_list(args.numeric_fields)
    baseline_id = args.baseline_id.strip() or default_baseline_id(args.mode)

    rows = normalize_rows(read_rows(in_csv), official_fields)
    source_count = len(rows)
    if args.mode == "official":
        rows = [r for r in rows if status_is_pass(r.get("all_pass_official", ""))]

    profiles = [
        {
            "dataset_id": r["dataset_id"],
            "seed": int(r["seed"]),
            "phi_scale": r["phi_scale"],
        }
        for r in rows
    ]

    if args.mode == "official":
        status_fields = list(dict.fromkeys(official_fields + ["all_pass_official"]))
    else:
        status_fields = [
            "g10_status",
            "g11_status",
            "g12_status",
            "g13_status",
            "g14_status",
            "g15_status",
            "g16_status",
            "g15b_v2_status",
            "all_pass_official",
            "all_pass_diagnostic",
            "all_pass",
        ]

    expected_rows: list[dict[str, Any]] = []
    for r in rows:
        rec: dict[str, Any] = {
            "dataset_id": r["dataset_id"],
            "seed": int(r["seed"]),
            "phi_scale": r["phi_scale"],
        }
        for field in status_fields + numeric_fields:
            rec[field] = r.get(field, "")
        expected_rows.append(rec)

    baseline = {
        "baseline_id": baseline_id,
        "baseline_mode": args.mode,
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "notes": [
            "Generated from run_qng_phi_scale_sweep_v1.py summary output.",
            "Housekeeping regression guard baseline only; no formula/threshold edits.",
            f"mode={args.mode}",
        ],
        "profiles": profiles,
        "compare": {
            "status_fields": status_fields,
            "numeric_fields": {field: {"abs_tol": args.abs_tol} for field in numeric_fields},
        },
        "expected_rows": expected_rows,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"wrote: {out_json}")
    print(f"mode: {args.mode}")
    print(f"source_profiles: {source_count}")
    print(f"profiles: {len(profiles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
