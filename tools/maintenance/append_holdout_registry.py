#!/usr/bin/env python3
"""
Append-only holdout registry writer.

Rules:
- never edits existing rows
- rejects duplicate holdout keys
- creates registry file with header if missing
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import sys


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "05_validation" / "pre-registrations" / "holdout-registry.csv"

FIELDNAMES = [
    "created_utc",
    "track_id",
    "model_version",
    "holdout_id",
    "prereg_file",
    "scope",
    "flyby_pass_ids",
    "pioneer_record_ids",
    "status",
    "notes",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Append a row to holdout-registry.csv (append-only).")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.add_argument("--track-id", required=True, help="e.g. C-086b2 or C-086b3")
    p.add_argument("--model-version", required=True, help="e.g. v1")
    p.add_argument("--holdout-id", required=True, help="e.g. H1")
    p.add_argument("--prereg-file", required=True, help="workspace-relative prereg file path")
    p.add_argument("--scope", choices=["holdout", "calibration"], default="holdout")
    p.add_argument("--flyby-pass-ids", required=True, help="Comma-separated pass IDs")
    p.add_argument("--pioneer-record-ids", default="", help="Comma-separated pioneer IDs")
    p.add_argument("--status", choices=["locked", "executed-pass", "executed-fail", "blocked"], default="locked")
    p.add_argument("--notes", default="")
    return p.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def holdout_key(track_id: str, version: str, holdout_id: str) -> str:
    return f"{track_id.strip()}::{version.strip()}::{holdout_id.strip()}"


def main() -> int:
    args = parse_args()
    registry = Path(args.registry)
    if not registry.is_absolute():
        registry = (ROOT / registry).resolve()

    existing = read_rows(registry)
    keys = {
        holdout_key(
            row.get("track_id", ""),
            row.get("model_version", ""),
            row.get("holdout_id", ""),
        )
        for row in existing
    }
    new_key = holdout_key(args.track_id, args.model_version, args.holdout_id)
    if new_key in keys:
        print(f"Duplicate holdout key already exists: {new_key}", file=sys.stderr)
        return 2

    row = {
        "created_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "track_id": args.track_id.strip(),
        "model_version": args.model_version.strip(),
        "holdout_id": args.holdout_id.strip(),
        "prereg_file": args.prereg_file.strip(),
        "scope": args.scope.strip(),
        "flyby_pass_ids": args.flyby_pass_ids.strip(),
        "pioneer_record_ids": args.pioneer_record_ids.strip(),
        "status": args.status.strip(),
        "notes": args.notes.strip(),
    }
    existing.append(row)
    write_rows(registry, existing)
    print(f"Appended holdout row: {new_key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

