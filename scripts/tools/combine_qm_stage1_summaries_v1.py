#!/usr/bin/env python3
"""
Combine multiple QM Stage-1 summary.csv files into one package.

Outputs:
- summary.csv
- dataset_summary.csv
- report.md
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Combine QM Stage-1 summary CSV files.")
    p.add_argument("--summary-csvs", required=True, help="Comma-separated list of summary.csv paths.")
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


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


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    parts = [Path(p).resolve() for p in parse_csv_list(args.summary_csvs)]
    if not parts:
        raise RuntimeError("no input summary CSVs provided")

    rows: list[dict[str, str]] = []
    for p in parts:
        if not p.exists():
            raise FileNotFoundError(f"missing summary csv: {p}")
        rows.extend(read_csv(p))
    if not rows:
        raise RuntimeError("combined input has zero rows")

    rows.sort(key=lambda r: (str(r.get("dataset_id", "")), int(str(r.get("seed", "0")))))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, list(rows[0].keys()))

    ds_rows: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in rows}):
        sub = [r for r in rows if str(r.get("dataset_id", "")) == ds]
        ds_rows.append(
            {
                "dataset_id": ds,
                "n_profiles": len(sub),
                "g17_pass": sum(1 for r in sub if norm_status(r.get("g17_status", "")) == "pass"),
                "g18_pass": sum(1 for r in sub if norm_status(r.get("g18_status", "")) == "pass"),
                "g19_pass": sum(1 for r in sub if norm_status(r.get("g19_status", "")) == "pass"),
                "g20_pass": sum(1 for r in sub if norm_status(r.get("g20_status", "")) == "pass"),
                "all_pass_qm_lane": sum(1 for r in sub if norm_status(r.get("all_pass_qm_lane", "")) == "pass"),
                "rc_fail_profiles": sum(
                    1
                    for r in sub
                    if any(int(str(r.get(k, "1"))) != 0 for k in ("g17_rc", "g18_rc", "g19_rc", "g20_rc"))
                ),
            }
        )
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    report_md = out_dir / "report.md"
    lines = [
        "# QM Stage-1 Combined Summary",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- input_parts: `{len(parts)}`",
        f"- profiles: `{len(rows)}`",
        "",
        "## Inputs",
        "",
    ]
    lines.extend([f"- `{p.as_posix()}`" for p in parts])
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
