#!/usr/bin/env python3
"""
Extract SPT-SZ Table-4 style cluster rows from markdown text produced by
scripts/extract_pdf_text.py.

Primary use:
- convert the SPT-SZ 2500 deg^2 catalog PDF text into a reusable CSV
  with cluster IDs + RA/Dec (+ detection significance xi).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import re


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "01_notes" / "source_text" / "spt-sz-galaxy-clusters.md"
DEFAULT_OUT = ROOT / "data" / "lensing" / "spt_sz_table4_catalog.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-spt-sz-catalog-extract.md"


@dataclass
class Entry:
    system_id: str
    raw_id_token: str
    ra_deg: float
    dec_deg: float
    xi: float
    source_line: int


def clean_minus(text: str) -> str:
    return (
        text.replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u00e2\u02c6\u2019", "-")
        .replace("\u00e2\u20ac\u201c", "-")
        .replace("\u00e2\u20ac\u201d", "-")
    )


def clean_id_token(text: str) -> str:
    t = clean_minus(text).strip()
    # Preferred path: extract canonical SPT token directly.
    m = re.search(r"J\d{4}-\d{4}[a-zA-Z]?", t)
    if m:
        t = m.group(0)
    else:
        # OCR fallback: keep only basic id-safe characters.
        t = "".join(ch for ch in t if ch.isalnum() or ch in {"-", "_"})
    t = t.replace("_", "-")
    return t.strip(" ,.;:")


def parse_float_token(token: str) -> float | None:
    t = clean_minus(token).strip()
    if not t:
        return None
    if t.startswith("."):
        t = "0" + t
    try:
        return float(t)
    except ValueError:
        return None


def consume_float(tokens: list[str], idx: int) -> tuple[float | None, int]:
    if idx >= len(tokens):
        return None, idx

    # Single-token float, e.g. "335.0809" or "-45.5824"
    direct = parse_float_token(tokens[idx])
    if direct is not None:
        return direct, idx + 1

    # Split decimal across two tokens, e.g. "335" ".0809"
    t0 = clean_minus(tokens[idx]).strip()
    if re.fullmatch(r"[-+]?\d+", t0) and (idx + 1) < len(tokens):
        t1 = clean_minus(tokens[idx + 1]).strip()
        if re.fullmatch(r"\.\d+", t1):
            merged = parse_float_token(t0 + t1)
            if merged is not None:
                return merged, idx + 2

    # Signed split decimal, e.g. "-" "45.5" (rare OCR style)
    if t0 in {"-", "+"} and (idx + 1) < len(tokens):
        merged = parse_float_token(t0 + clean_minus(tokens[idx + 1]).strip())
        if merged is not None:
            return merged, idx + 2

    return None, idx


def normalize_id(raw_id_token: str) -> str:
    tid = clean_id_token(raw_id_token)
    # Remove single trailing footnote letter, e.g. J0522-4818a -> J0522-4818
    if re.fullmatch(r"J\d{4}-\d{4}[a-z]$", tid):
        tid = tid[:-1]
    return f"SPT-CL {tid}"


def parse_line(line: str, line_no: int) -> Entry | None:
    s = line.strip()
    if not s.startswith("SPT-CL "):
        return None

    tokens = s.split()
    if len(tokens) < 6:
        return None
    # Expected leading tokens: "SPT-CL" "Jxxxx-xxxx..."
    if tokens[0] != "SPT-CL":
        return None
    raw_id_token = tokens[1]

    idx = 2
    ra, idx = consume_float(tokens, idx)
    dec, idx = consume_float(tokens, idx)
    xi, idx = consume_float(tokens, idx)

    # Table-5 rows are filtered out because they do not have numeric RA/Dec at token 2+.
    if ra is None or dec is None or xi is None:
        return None

    # Basic sanity bounds for Table-4 SPT rows.
    if not (0.0 <= ra <= 360.0):
        return None
    if not (-90.0 <= dec <= 90.0):
        return None
    if not (0.0 <= xi <= 100.0):
        return None

    return Entry(
        system_id=normalize_id(raw_id_token),
        raw_id_token=clean_id_token(raw_id_token),
        ra_deg=float(ra),
        dec_deg=float(dec),
        xi=float(xi),
        source_line=line_no,
    )


def parse_entries(md_path: Path) -> tuple[list[Entry], int]:
    entries: list[Entry] = []
    scanned = 0
    for line_no, line in enumerate(md_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        scanned += 1
        e = parse_line(line, line_no)
        if e is not None:
            entries.append(e)
    return entries, scanned


def dedupe(entries: list[Entry]) -> tuple[list[Entry], int]:
    by_id: dict[str, Entry] = {}
    duplicate_rows = 0
    for e in entries:
        prev = by_id.get(e.system_id)
        if prev is None:
            by_id[e.system_id] = e
            continue
        duplicate_rows += 1
        # Keep the one with higher xi in case of OCR repeats/variants.
        if e.xi > prev.xi:
            by_id[e.system_id] = e
    deduped = sorted(by_id.values(), key=lambda x: x.system_id)
    return deduped, duplicate_rows


def write_csv(path: Path, rows: list[Entry]) -> None:
    fields = [
        "system_id",
        "ra_deg",
        "dec_deg",
        "xi",
        "raw_id_token",
        "source_line",
        "source",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "system_id": r.system_id,
                    "ra_deg": f"{r.ra_deg:.10f}",
                    "dec_deg": f"{r.dec_deg:.10f}",
                    "xi": f"{r.xi:.6f}",
                    "raw_id_token": r.raw_id_token,
                    "source_line": str(r.source_line),
                    "source": "SPT-SZ 2500 deg^2 PDF Table 4 text extraction",
                }
            )


def write_report(
    path: Path,
    *,
    input_md: Path,
    out_csv: Path,
    scanned_lines: int,
    raw_count: int,
    unique_count: int,
    duplicate_rows: int,
    xi_min: float,
    xi_max: float,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# DS-006 SPT-SZ Catalog Extraction",
        "",
        f"- Generated (UTC): {ts}",
        f"- Input markdown: `{input_md}`",
        f"- Output CSV: `{out_csv}`",
        "",
        "## Summary",
        "",
        f"- Scanned lines: `{scanned_lines}`",
        f"- Parsed candidate rows: `{raw_count}`",
        f"- Unique systems after dedupe: `{unique_count}`",
        f"- Duplicate rows dropped: `{duplicate_rows}`",
        f"- xi range: `[{xi_min:.3f}, {xi_max:.3f}]`",
        "",
        "## DS-006 Use",
        "",
        "- This file provides one center per cluster (SPT/SZ selection position).",
        "- It is suitable as one side of cross-match (e.g., lensing/SZ side).",
        "- It does not by itself provide baryon-vs-lensing offset pairs; combine with an X-ray/baryonic-center catalog.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract SPT-SZ Table-4 catalog rows from markdown text.")
    p.add_argument("--input-md", default=str(DEFAULT_INPUT), help="Input markdown path.")
    p.add_argument("--out-csv", default=str(DEFAULT_OUT), help="Output CSV path.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT), help="Output markdown report path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    input_md = Path(args.input_md)
    out_csv = Path(args.out_csv)
    report_out = Path(args.report_out)

    if not input_md.is_absolute():
        input_md = (ROOT / input_md).resolve()
    if not out_csv.is_absolute():
        out_csv = (ROOT / out_csv).resolve()
    if not report_out.is_absolute():
        report_out = (ROOT / report_out).resolve()

    if not input_md.exists():
        raise FileNotFoundError(f"Input markdown not found: {input_md}")

    raw_entries, scanned_lines = parse_entries(input_md)
    if not raw_entries:
        raise RuntimeError("No SPT rows parsed. Check input markdown quality.")

    deduped, duplicate_rows = dedupe(raw_entries)
    write_csv(out_csv, deduped)
    xis = [r.xi for r in deduped]
    write_report(
        report_out,
        input_md=input_md,
        out_csv=out_csv,
        scanned_lines=scanned_lines,
        raw_count=len(raw_entries),
        unique_count=len(deduped),
        duplicate_rows=duplicate_rows,
        xi_min=min(xis),
        xi_max=max(xis),
    )

    print(f"Scanned lines: {scanned_lines}")
    print(f"Parsed rows: {len(raw_entries)} | unique: {len(deduped)} | duplicates: {duplicate_rows}")
    print(f"Output CSV: {out_csv}")
    print(f"Report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
