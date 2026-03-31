#!/usr/bin/env python3
"""
Extract MCXC cluster positions from CDS fixed-width file.

Input:
- mcxc.dat from CDS (J/A+A/534/A109)

Output:
- CSV with RA/Dec and metadata suitable for DS-006 cross-match workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "lensing" / "mcxc_full_from_cds.dat"
DEFAULT_OUT = ROOT / "data" / "lensing" / "mcxc_catalog_full.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-mcxc-catalog-extract.md"


@dataclass
class Row:
    system_id: str
    ra_deg: float
    dec_deg: float
    z: float
    catalog: str
    sub_catalog: str


def field(line: str, start: int, end: int) -> str:
    return line[start - 1 : end].strip()


def safe_float(text: str) -> float | None:
    t = text.strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def parse_line(line: str) -> Row | None:
    if not line.strip():
        return None

    mcxc = field(line, 1, 12)
    ra_deg = safe_float(field(line, 109, 115))
    dec_deg = safe_float(field(line, 117, 123))
    z = safe_float(field(line, 141, 146))
    cat = field(line, 148, 159)
    sub_cat = field(line, 161, 172)

    if not mcxc:
        return None
    if ra_deg is None or dec_deg is None:
        return None
    if z is None:
        z = 0.0

    return Row(
        system_id=f"MCXC {mcxc}",
        ra_deg=float(ra_deg),
        dec_deg=float(dec_deg),
        z=float(z),
        catalog=cat,
        sub_catalog=sub_cat,
    )


def parse_rows(path: Path) -> tuple[list[Row], int]:
    rows: list[Row] = []
    scanned = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        scanned += 1
        row = parse_line(line)
        if row is not None:
            rows.append(row)
    return rows, scanned


def write_csv(path: Path, rows: list[Row]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "ra_deg", "dec_deg", "z", "catalog", "sub_catalog", "source"])
        for r in rows:
            w.writerow(
                [
                    r.system_id,
                    f"{r.ra_deg:.6f}",
                    f"{r.dec_deg:.6f}",
                    f"{r.z:.6f}",
                    r.catalog,
                    r.sub_catalog,
                    "MCXC CDS J/A+A/534/A109 (mcxc.dat)",
                ]
            )


def write_report(
    path: Path,
    *,
    input_dat: Path,
    out_csv: Path,
    scanned_lines: int,
    parsed_rows: int,
    ra_min: float,
    ra_max: float,
    dec_min: float,
    dec_max: float,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# DS-006 MCXC Catalog Extraction",
        "",
        f"- Generated (UTC): {ts}",
        f"- Input data: `{input_dat}`",
        f"- Output CSV: `{out_csv}`",
        "",
        "## Summary",
        "",
        f"- Scanned lines: `{scanned_lines}`",
        f"- Parsed rows: `{parsed_rows}`",
        f"- RA range (deg): `[{ra_min:.3f}, {ra_max:.3f}]`",
        f"- Dec range (deg): `[{dec_min:.3f}, {dec_max:.3f}]`",
        "",
        "## DS-006 Use",
        "",
        "- This file is a baryonic/X-ray side catalog (cluster centers).",
        "- Use together with SZ/lensing side catalogs (e.g., SPT-SZ Table-4) in cross-match builder.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract MCXC CDS fixed-width catalog to CSV.")
    p.add_argument("--input-dat", default=str(DEFAULT_INPUT), help="Path to CDS mcxc.dat file.")
    p.add_argument("--out-csv", default=str(DEFAULT_OUT), help="Output CSV path.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT), help="Output markdown report path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    input_dat = Path(args.input_dat)
    out_csv = Path(args.out_csv)
    report_out = Path(args.report_out)

    if not input_dat.is_absolute():
        input_dat = (ROOT / input_dat).resolve()
    if not out_csv.is_absolute():
        out_csv = (ROOT / out_csv).resolve()
    if not report_out.is_absolute():
        report_out = (ROOT / report_out).resolve()

    if not input_dat.exists():
        raise FileNotFoundError(f"Input mcxc.dat not found: {input_dat}")

    rows, scanned = parse_rows(input_dat)
    if not rows:
        raise RuntimeError("No rows parsed from mcxc.dat.")

    write_csv(out_csv, rows)
    ra_vals = [r.ra_deg for r in rows]
    dec_vals = [r.dec_deg for r in rows]
    write_report(
        report_out,
        input_dat=input_dat,
        out_csv=out_csv,
        scanned_lines=scanned,
        parsed_rows=len(rows),
        ra_min=min(ra_vals),
        ra_max=max(ra_vals),
        dec_min=min(dec_vals),
        dec_max=max(dec_vals),
    )

    print(f"Scanned lines: {scanned}")
    print(f"Parsed rows: {len(rows)}")
    print(f"Output CSV: {out_csv}")
    print(f"Report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
