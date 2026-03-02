#!/usr/bin/env python3
"""Build Stage-2 regression baseline JSON from Stage-2 official summary."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_STATUS_FIELDS = [
    "g10_status",
    "g11_status",
    "g12_status",
    "g7_status",
    "lane_3p1_status",
    "lane_strong_field_status",
    "lane_tensor_status",
    "stage2_status",
]


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Stage-2 baseline JSON from official summary.csv.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--baseline-id", default="gr-stage2-official-baseline-v1")
    p.add_argument("--effective-tag", default="gr-stage2-g11-v4-official")
    p.add_argument("--effective-commit", default="")
    p.add_argument("--effective-date-utc", default="")
    p.add_argument("--status-fields", default=",".join(DEFAULT_STATUS_FIELDS))
    return p.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_json = Path(args.out_json).resolve()
    status_fields = parse_csv_list(args.status_fields)

    rows = read_rows(summary_csv)
    if not rows:
        raise RuntimeError(f"summary has zero rows: {summary_csv}")

    rows.sort(key=lambda r: (r.get("dataset_id", ""), int(r.get("seed", "0"))))

    profiles: list[dict[str, object]] = []
    expected_rows: list[dict[str, object]] = []
    for r in rows:
        ds = r["dataset_id"].strip()
        seed = int(r["seed"])
        profiles.append({"dataset_id": ds, "seed": seed})
        rec: dict[str, object] = {"dataset_id": ds, "seed": seed}
        for field in status_fields:
            rec[field] = r.get(field, "")
        expected_rows.append(rec)

    baseline = {
        "baseline_id": args.baseline_id,
        "effective_tag": args.effective_tag,
        "effective_commit": args.effective_commit,
        "effective_date_utc": args.effective_date_utc,
        "notes": [
            "Generated from Stage-2 official policy summary.",
            "Status-only guard baseline for Stage-2 governance mapping.",
        ],
        "profiles": profiles,
        "compare": {
            "status_fields": status_fields,
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
