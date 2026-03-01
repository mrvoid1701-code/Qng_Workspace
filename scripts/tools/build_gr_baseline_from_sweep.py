#!/usr/bin/env python3
"""
Build a GR regression baseline JSON from phi-scale sweep summary.csv.

Housekeeping helper:
- stdlib only
- no scientific logic changes
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build GR baseline JSON from sweep summary CSV.")
    p.add_argument("--summary-csv", required=True, help="Input summary.csv from run_qng_phi_scale_sweep_v1.py")
    p.add_argument("--out-json", required=True, help="Output baseline JSON path")
    p.add_argument("--baseline-id", default="gr-g10-g16-regression-grid20-v1")
    p.add_argument("--effective-tag", default="gr-ppn-g15b-v2-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument("--abs-tol", type=float, default=1e-6)
    return p.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    in_csv = Path(args.summary_csv).resolve()
    out_json = Path(args.out_json).resolve()

    rows = read_rows(in_csv)
    rows.sort(key=lambda r: (r["dataset_id"], int(r["seed"]), float(r["phi_scale"])))

    profiles = [
        {
            "dataset_id": r["dataset_id"],
            "seed": int(r["seed"]),
            "phi_scale": f"{float(r['phi_scale']):.2f}",
        }
        for r in rows
    ]

    status_fields = [
        "g10_status",
        "g11_status",
        "g12_status",
        "g13_status",
        "g14_status",
        "g15_status",
        "g16_status",
        "g15b_v2_status",
        "all_pass",
    ]
    numeric_fields = [
        "g15a_gamma_dev",
        "g15d_ep_ratio",
        "g15b_shapiro_ratio",
        "g15b_v2_shapiro_ratio",
        "g13b_e_cov_drift",
        "g14b_e_cov_drift",
        "g13c_speed_reduction",
    ]

    expected_rows: list[dict[str, Any]] = []
    for r in rows:
        rec: dict[str, Any] = {
            "dataset_id": r["dataset_id"],
            "seed": int(r["seed"]),
            "phi_scale": f"{float(r['phi_scale']):.2f}",
        }
        for field in status_fields + numeric_fields:
            rec[field] = r.get(field, "")
        expected_rows.append(rec)

    baseline = {
        "baseline_id": args.baseline_id,
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "notes": [
            "Generated from run_qng_phi_scale_sweep_v1.py summary output.",
            "Housekeeping regression guard baseline only; no formula/threshold edits.",
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
    print(f"profiles: {len(profiles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

