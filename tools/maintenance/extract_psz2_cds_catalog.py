#!/usr/bin/env python3
"""
Extract Planck PSZ2 catalog positions from CDS fixed-width file.

Input:
- psz2.dat from CDS (J/A+A/594/A27)

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
DEFAULT_INPUT = ROOT / "data" / "lensing" / "psz2_full_from_cds.dat"
DEFAULT_OUT = ROOT / "data" / "lensing" / "psz2_catalog_full.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-psz2-catalog-extract.md"


@dataclass
class Row:
    system_id: str
    ra_deg: float
    dec_deg: float
    snr: float
    z: float
    planck_name: str
    mcxc_cross_id: str
    act_cross_id: str
    spt_cross_id: str


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

    planck_name = field(line, 6, 23)
    ra_deg = safe_float(field(line, 49, 59))
    dec_deg = safe_float(field(line, 61, 71))
    snr = safe_float(field(line, 83, 90))
    z = safe_float(field(line, 168, 176))
    mcxc = field(line, 206, 217)
    act = field(line, 240, 258)
    spt = field(line, 260, 275)

    if not planck_name or ra_deg is None or dec_deg is None:
        return None
    if snr is None:
        snr = 0.0
    if z is None:
        z = -1.0

    # Prefer MCXC-linked ID for deterministic matching to MCXC baryonic catalog.
    if mcxc:
        system_id = f"MCXC {mcxc}"
    else:
        system_id = f"PSZ2 {planck_name}"

    return Row(
        system_id=system_id,
        ra_deg=float(ra_deg),
        dec_deg=float(dec_deg),
        snr=float(snr),
        z=float(z),
        planck_name=planck_name,
        mcxc_cross_id=mcxc,
        act_cross_id=act,
        spt_cross_id=spt,
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
        w.writerow(
            [
                "system_id",
                "ra_deg",
                "dec_deg",
                "snr",
                "z",
                "planck_name",
                "mcxc_cross_id",
                "act_cross_id",
                "spt_cross_id",
                "source",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.system_id,
                    f"{r.ra_deg:.7f}",
                    f"{r.dec_deg:.7f}",
                    f"{r.snr:.5f}",
                    f"{r.z:.6f}",
                    r.planck_name,
                    r.mcxc_cross_id,
                    r.act_cross_id,
                    r.spt_cross_id,
                    "Planck PSZ2 CDS J/A+A/594/A27 (psz2.dat)",
                ]
            )


def write_report(
    path: Path,
    *,
    input_dat: Path,
    out_csv: Path,
    scanned_lines: int,
    parsed_rows: int,
    mcxc_linked_rows: int,
    ra_min: float,
    ra_max: float,
    dec_min: float,
    dec_max: float,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# DS-006 PSZ2 Catalog Extraction",
        "",
        f"- Generated (UTC): {ts}",
        f"- Input data: `{input_dat}`",
        f"- Output CSV: `{out_csv}`",
        "",
        "## Summary",
        "",
        f"- Scanned lines: `{scanned_lines}`",
        f"- Parsed rows: `{parsed_rows}`",
        f"- Rows with MCXC cross-id: `{mcxc_linked_rows}`",
        f"- RA range (deg): `[{ra_min:.3f}, {ra_max:.3f}]`",
        f"- Dec range (deg): `[{dec_min:.3f}, {dec_max:.3f}]`",
        "",
        "## DS-006 Use",
        "",
        "- This file provides SZ-side cluster centers from Planck PSZ2.",
        "- If `mcxc_cross_id` exists, `system_id` is normalized as `MCXC J...` for direct MCXC id matching.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract Planck PSZ2 CDS fixed-width catalog to CSV.")
    p.add_argument("--input-dat", default=str(DEFAULT_INPUT), help="Path to CDS psz2.dat file.")
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
        raise FileNotFoundError(f"Input psz2.dat not found: {input_dat}")

    rows, scanned = parse_rows(input_dat)
    if not rows:
        raise RuntimeError("No rows parsed from psz2.dat.")

    write_csv(out_csv, rows)
    ra_vals = [r.ra_deg for r in rows]
    dec_vals = [r.dec_deg for r in rows]
    mcxc_linked_rows = sum(1 for r in rows if r.mcxc_cross_id)
    write_report(
        report_out,
        input_dat=input_dat,
        out_csv=out_csv,
        scanned_lines=scanned,
        parsed_rows=len(rows),
        mcxc_linked_rows=mcxc_linked_rows,
        ra_min=min(ra_vals),
        ra_max=max(ra_vals),
        dec_min=min(dec_vals),
        dec_max=max(dec_vals),
    )

    print(f"Scanned lines: {scanned}")
    print(f"Parsed rows: {len(rows)}")
    print(f"MCXC cross-id rows: {mcxc_linked_rows}")
    print(f"Output CSV: {out_csv}")
    print(f"Report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
