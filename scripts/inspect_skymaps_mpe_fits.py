#!/usr/bin/env python3
"""
Inspect SKYMAPS_052022_MPE.fits without external dependencies.

Outputs:
- data/lensing/skymaps_052022_mpe_tiles.csv
- 05_validation/evidence/artifacts/ds006-skymaps-mpe-inspection.md

This script parses the first BINTABLE extension using FITS big-endian binary rules
for the known column layout present in SKYMAPS_052022_MPE.fits.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import statistics
import struct


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = Path.home() / "Downloads" / "SKYMAPS_052022_MPE.fits"
DEFAULT_CSV_OUT = ROOT / "data" / "lensing" / "skymaps_052022_mpe_tiles.csv"
DEFAULT_REPORT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-skymaps-mpe-inspection.md"


@dataclass
class TableMeta:
    row_len: int
    row_count: int
    data_offset: int
    tfields: int
    col_names: list[str]
    col_forms: list[str]
    col_units: list[str]
    header: dict[str, str]


def parse_cards(block: bytes) -> list[str]:
    out: list[str] = []
    for i in range(0, len(block), 80):
        c = block[i : i + 80]
        if len(c) < 80:
            break
        out.append(c.decode("ascii", errors="replace"))
    return out


def parse_header(data: bytes, offset: int) -> tuple[dict[str, str], int]:
    header_bytes = bytearray()
    off = offset
    while True:
        block = data[off : off + 2880]
        if len(block) < 2880:
            raise RuntimeError("Unexpected EOF while reading FITS header.")
        header_bytes.extend(block)
        off += 2880
        cards = parse_cards(block)
        if any(c.startswith("END") for c in cards):
            break

    kv: dict[str, str] = {}
    for card in parse_cards(bytes(header_bytes)):
        key = card[:8].strip()
        if not key or key == "END":
            continue
        if card[8:10] == "= ":
            raw_val = card[10:80].split("/")[0].strip()
            kv[key] = raw_val.strip("'")
    return kv, off


def data_block_size(header: dict[str, str]) -> int:
    xtension = header.get("XTENSION", "PRIMARY").strip()
    naxis = int(header.get("NAXIS", "0"))
    bitpix = int(header.get("BITPIX", "8"))
    pcount = int(header.get("PCOUNT", "0"))
    gcount = int(header.get("GCOUNT", "1"))

    if naxis == 0:
        size = 0
    elif xtension == "BINTABLE":
        n1 = int(header.get("NAXIS1", "0"))
        n2 = int(header.get("NAXIS2", "0"))
        size = n1 * n2 + pcount
    else:
        n = 1
        for i in range(1, naxis + 1):
            n *= int(header.get(f"NAXIS{i}", "1"))
        size = n * abs(bitpix) // 8 + pcount
    size *= gcount
    return size


def locate_first_bintable(data: bytes) -> TableMeta:
    off = 0
    hdu = 0
    while off < len(data):
        hdr, hdr_end = parse_header(data, off)
        dsize = data_block_size(hdr)

        if hdr.get("XTENSION", "").strip() == "BINTABLE":
            tfields = int(hdr.get("TFIELDS", "0"))
            names: list[str] = []
            forms: list[str] = []
            units: list[str] = []
            for i in range(1, tfields + 1):
                names.append(hdr.get(f"TTYPE{i}", "").strip())
                forms.append(hdr.get(f"TFORM{i}", "").strip())
                units.append(hdr.get(f"TUNIT{i}", "").strip())
            return TableMeta(
                row_len=int(hdr.get("NAXIS1", "0")),
                row_count=int(hdr.get("NAXIS2", "0")),
                data_offset=hdr_end,
                tfields=tfields,
                col_names=names,
                col_forms=forms,
                col_units=units,
                header=hdr,
            )

        pad = ((dsize + 2879) // 2880) * 2880
        off = hdr_end + pad
        hdu += 1

    raise RuntimeError("No BINTABLE extension found.")


def struct_format_from_tforms(tforms: list[str]) -> str:
    # Only forms present in this FITS are expected: J (int32), I (int16), D (float64)
    # FITS uses big-endian.
    out = [">"]
    for form in tforms:
        f = form.strip().upper()
        if f.endswith("J"):
            repeat = int(f[:-1]) if f[:-1] else 1
            out.append("i" * repeat)
        elif f.endswith("I"):
            repeat = int(f[:-1]) if f[:-1] else 1
            out.append("h" * repeat)
        elif f.endswith("D"):
            repeat = int(f[:-1]) if f[:-1] else 1
            out.append("d" * repeat)
        else:
            raise RuntimeError(f"Unsupported TFORM '{form}' for stdlib parser.")
    return "".join(out)


def read_rows(data: bytes, meta: TableMeta) -> list[tuple]:
    fmt = struct_format_from_tforms(meta.col_forms)
    if struct.calcsize(fmt) != meta.row_len:
        raise RuntimeError(
            f"Row length mismatch. calcsize={struct.calcsize(fmt)} header={meta.row_len}"
        )

    out: list[tuple] = []
    start = meta.data_offset
    for i in range(meta.row_count):
        row = data[start + i * meta.row_len : start + (i + 1) * meta.row_len]
        if len(row) < meta.row_len:
            break
        out.append(struct.unpack(fmt, row))
    return out


def write_csv(path: Path, col_names: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(col_names)
        for r in rows:
            w.writerow(list(r))


def write_report(path: Path, input_fits: Path, csv_out: Path, meta: TableMeta, rows: list[tuple]) -> None:
    idx = {name: i for i, name in enumerate(meta.col_names)}

    def col_stats(name: str) -> tuple[float, float, float]:
        col = [float(r[idx[name]]) for r in rows]
        return min(col), max(col), statistics.fmean(col)

    ra_min = col_stats("RA_MIN")
    ra_max = col_stats("RA_MAX")
    de_min = col_stats("DE_MIN")
    de_max = col_stats("DE_MAX")
    n_nbrs = col_stats("N_NBRS")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# DS-006 SKYMAPS_052022_MPE Inspection",
        "",
        f"- Generated (UTC): {now}",
        f"- Input FITS: `{input_fits}`",
        f"- Output CSV: `{csv_out}`",
        "",
        "## FITS Structure",
        "",
        f"- EXTNAME: `{meta.header.get('EXTNAME', '')}`",
        f"- Rows: `{meta.row_count}`",
        f"- Columns: `{meta.tfields}`",
        f"- Row length (bytes): `{meta.row_len}`",
        "",
        "## Column Summary",
        "",
        "| Name | TFORM | Unit |",
        "| --- | --- | --- |",
    ]
    for name, form, unit in zip(meta.col_names, meta.col_forms, meta.col_units):
        lines.append(f"| `{name}` | `{form}` | `{unit}` |")

    lines += [
        "",
        "## Numeric Coverage",
        "",
        f"- RA_MIN range: `{ra_min[0]:.6f}` .. `{ra_min[1]:.6f}` (mean `{ra_min[2]:.6f}`)",
        f"- RA_MAX range: `{ra_max[0]:.6f}` .. `{ra_max[1]:.6f}` (mean `{ra_max[2]:.6f}`)",
        f"- DE_MIN range: `{de_min[0]:.6f}` .. `{de_min[1]:.6f}` (mean `{de_min[2]:.6f}`)",
        f"- DE_MAX range: `{de_max[0]:.6f}` .. `{de_max[1]:.6f}` (mean `{de_max[2]:.6f}`)",
        f"- N_NBRS range: `{n_nbrs[0]:.0f}` .. `{n_nbrs[1]:.0f}` (mean `{n_nbrs[2]:.3f}`)",
        "",
        "## DS-006 Relevance",
        "",
        "- This file is a sky-tiling/index table (map cells and neighbors), not a direct cluster-offset catalog.",
        "- It does not contain explicit baryonic-center vs lensing-center paired measurements per cluster.",
        "- Therefore it can be used as supporting sky-map metadata, but not as final `gold` DS-006 lensing evidence by itself.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inspect SKYMAPS_052022_MPE.fits and export table to CSV.")
    p.add_argument("--input-fits", default=str(DEFAULT_INPUT), help="Input FITS path.")
    p.add_argument("--csv-out", default=str(DEFAULT_CSV_OUT), help="Output CSV path.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT_OUT), help="Output markdown report path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    fits_path = Path(args.input_fits)
    if not fits_path.exists():
        raise FileNotFoundError(f"Input FITS not found: {fits_path}")

    data = fits_path.read_bytes()
    meta = locate_first_bintable(data)
    rows = read_rows(data, meta)
    if len(rows) != meta.row_count:
        raise RuntimeError(f"Parsed row count mismatch: parsed={len(rows)} expected={meta.row_count}")

    csv_out = Path(args.csv_out)
    if not csv_out.is_absolute():
        csv_out = (ROOT / csv_out).resolve()
    report_out = Path(args.report_out)
    if not report_out.is_absolute():
        report_out = (ROOT / report_out).resolve()

    write_csv(csv_out, meta.col_names, rows)
    write_report(report_out, fits_path, csv_out, meta, rows)

    print(f"Rows parsed: {len(rows)}")
    print(f"CSV written: {csv_out}")
    print(f"Report written: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
