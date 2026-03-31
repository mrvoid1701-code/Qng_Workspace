#!/usr/bin/env python3
"""Parse HELIOWeb mission-minus-Earth hourly listings into structured CSVs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List


ROW_RE = re.compile(
    r"^\s*(\d{4})\s+(\d{1,3})\s+(\d{1,2})\s+([\-0-9.]+)\s+([\-0-9.]+)\s+([\-0-9.]+)\s+([\-0-9.]+)\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse HELIOWeb mission-vs-Earth hourly outputs."
    )
    parser.add_argument(
        "--glob",
        default="data/trajectory/sources/helioweb/*_helios2h_vs_earth.txt",
        help="Input file glob",
    )
    parser.add_argument(
        "--detail-out",
        default="data/trajectory/sources/helioweb/holdout_vs_earth_hourly.csv",
        help="Detailed per-hour output CSV",
    )
    parser.add_argument(
        "--summary-out",
        default="data/trajectory/sources/helioweb/holdout_vs_earth_summary.csv",
        help="Summary per-file output CSV",
    )
    return parser.parse_args()


def infer_pass_id(stem: str) -> str:
    low = stem.lower()
    if low.startswith("juno_"):
        return "JUNO_1"
    if low.startswith("bepicolombo_"):
        return "BEPICOLOMBO_1"
    if low.startswith("solar_orbiter_"):
        return "SOLAR_ORBITER_1"
    return stem.upper()


def parse_file(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        year, day, hour, rad_au, se_lat, se_lon, dist = m.groups()
        rows.append(
            {
                "year": int(year),
                "day": int(day),
                "hour": int(hour),
                "rad_au": float(rad_au),
                "se_lat_deg": float(se_lat),
                "se_lon_deg": float(se_lon),
                "distance_au": float(dist),
            }
        )
    return rows


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    files = sorted(Path(".").glob(args.glob))
    detail_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for file_path in files:
        parsed = parse_file(file_path)
        if not parsed:
            continue
        pass_id = infer_pass_id(file_path.stem)
        for r in parsed:
            detail_rows.append(
                {
                    "source_file": str(file_path).replace("\\", "/"),
                    "pass_id": pass_id,
                    **r,
                }
            )

        min_row = min(parsed, key=lambda x: x["distance_au"])
        summary_rows.append(
            {
                "source_file": str(file_path).replace("\\", "/"),
                "pass_id": pass_id,
                "year": min_row["year"],
                "day": min_row["day"],
                "hour_at_min_distance": min_row["hour"],
                "min_distance_au": f"{min_row['distance_au']:.6f}",
                "rad_au_at_min_distance": f"{min_row['rad_au']:.6f}",
                "se_lat_deg_at_min_distance": f"{min_row['se_lat_deg']:.6f}",
                "se_lon_deg_at_min_distance": f"{min_row['se_lon_deg']:.6f}",
                "n_hour_rows": len(parsed),
            }
        )

    write_csv(
        Path(args.detail_out),
        detail_rows,
        [
            "source_file",
            "pass_id",
            "year",
            "day",
            "hour",
            "rad_au",
            "se_lat_deg",
            "se_lon_deg",
            "distance_au",
        ],
    )
    write_csv(
        Path(args.summary_out),
        summary_rows,
        [
            "source_file",
            "pass_id",
            "year",
            "day",
            "hour_at_min_distance",
            "min_distance_au",
            "rad_au_at_min_distance",
            "se_lat_deg_at_min_distance",
            "se_lon_deg_at_min_distance",
            "n_hour_rows",
        ],
    )

    print(f"Parsed files: {len(files)}")
    print(f"Wrote detail CSV: {args.detail_out}")
    print(f"Wrote summary CSV: {args.summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
