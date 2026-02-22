#!/usr/bin/env python3
"""
Inspect eROSITA all-sky rates-map FITS files (primary image HDU only).

Designed for files like:
- e01_TM8_0.200_0.400keV_3arcm_c947_AIT_sum_Ratesmap.fits
- e01_TM8_0.400_0.600keV_3arcm_c947_AIT_sum_Ratesmap.fits

Outputs:
- data/lensing/erosita_tm8_ratesmap_summary.csv
- 05_validation/evidence/artifacts/ds006-erosita-ratesmap-assessment.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import array
import csv
import math


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOW = Path.home() / "Downloads" / "e01_TM8_0.200_0.400keV_3arcm_c947_AIT_sum_Ratesmap.fits"
DEFAULT_MID = Path.home() / "Downloads" / "e01_TM8_0.400_0.600keV_3arcm_c947_AIT_sum_Ratesmap.fits"
DEFAULT_SUMMARY = ROOT / "data" / "lensing" / "erosita_tm8_ratesmap_summary.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-erosita-ratesmap-assessment.md"


@dataclass
class FitsImageMeta:
    path: Path
    bitpix: int
    naxis1: int
    naxis2: int
    ctype1: str
    ctype2: str
    crval1: float
    crval2: float
    crpix1: float
    crpix2: float
    cdelt1: float
    cdelt2: float
    telescope: str
    data_offset: int
    data_bytes: int


@dataclass
class Stats:
    finite: int
    nan: int
    inf: int
    min_v: float
    max_v: float
    mean_v: float
    std_v: float
    p99_v: float
    p999_v: float


def parse_cards(block: bytes) -> list[str]:
    out: list[str] = []
    for i in range(0, len(block), 80):
        card = block[i : i + 80]
        if len(card) < 80:
            break
        out.append(card.decode("ascii", errors="replace"))
    return out


def parse_header(data: bytes, offset: int) -> tuple[dict[str, str], int]:
    header = bytearray()
    off = offset
    while True:
        block = data[off : off + 2880]
        if len(block) < 2880:
            raise RuntimeError("Unexpected EOF while reading FITS header.")
        header.extend(block)
        off += 2880
        cards = parse_cards(block)
        if any(c.startswith("END") for c in cards):
            break

    kv: dict[str, str] = {}
    for card in parse_cards(bytes(header)):
        key = card[:8].strip()
        if not key or key == "END":
            continue
        if card[8:10] == "= ":
            kv[key] = card[10:80].split("/")[0].strip().strip("'")
    return kv, off


def inspect_primary_image(path: Path) -> FitsImageMeta:
    raw = path.read_bytes()
    hdr, data_offset = parse_header(raw, 0)

    xtension = hdr.get("XTENSION", "").strip()
    if xtension:
        raise RuntimeError(f"{path.name}: expected primary image HDU, got XTENSION={xtension}")

    bitpix = int(hdr.get("BITPIX", "0"))
    naxis = int(hdr.get("NAXIS", "0"))
    if naxis != 2:
        raise RuntimeError(f"{path.name}: expected 2D image, got NAXIS={naxis}")
    n1 = int(hdr.get("NAXIS1", "0"))
    n2 = int(hdr.get("NAXIS2", "0"))
    data_bytes = n1 * n2 * abs(bitpix) // 8

    return FitsImageMeta(
        path=path,
        bitpix=bitpix,
        naxis1=n1,
        naxis2=n2,
        ctype1=hdr.get("CTYPE1", ""),
        ctype2=hdr.get("CTYPE2", ""),
        crval1=float(hdr.get("CRVAL1", "nan")),
        crval2=float(hdr.get("CRVAL2", "nan")),
        crpix1=float(hdr.get("CRPIX1", "nan")),
        crpix2=float(hdr.get("CRPIX2", "nan")),
        cdelt1=float(hdr.get("CDELT1", "nan")),
        cdelt2=float(hdr.get("CDELT2", "nan")),
        telescope=hdr.get("TELESCOP", ""),
        data_offset=data_offset,
        data_bytes=data_bytes,
    )


def load_float_image(meta: FitsImageMeta) -> array.array:
    raw = meta.path.read_bytes()
    chunk = raw[meta.data_offset : meta.data_offset + meta.data_bytes]
    if len(chunk) != meta.data_bytes:
        raise RuntimeError(f"{meta.path.name}: image payload size mismatch.")
    arr = array.array("f")
    arr.frombytes(chunk)
    # FITS stores big-endian; Windows x86 is little-endian.
    arr.byteswap()
    return arr


def percentile_from_sorted(vals: list[float], q: float) -> float:
    if not vals:
        return float("nan")
    idx = int(round((len(vals) - 1) * q))
    idx = max(0, min(len(vals) - 1, idx))
    return vals[idx]


def compute_stats(values: array.array) -> Stats:
    finite_vals: list[float] = []
    n_nan = 0
    n_inf = 0
    s = 0.0
    s2 = 0.0
    mn = float("inf")
    mx = float("-inf")

    for v in values:
        if math.isnan(v):
            n_nan += 1
            continue
        if math.isinf(v):
            n_inf += 1
            continue
        fv = float(v)
        finite_vals.append(fv)
        s += fv
        s2 += fv * fv
        if fv < mn:
            mn = fv
        if fv > mx:
            mx = fv

    n = len(finite_vals)
    if n == 0:
        return Stats(0, n_nan, n_inf, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))

    mean_v = s / n
    var_v = max(0.0, s2 / n - mean_v * mean_v)
    std_v = math.sqrt(var_v)
    finite_vals.sort()
    p99 = percentile_from_sorted(finite_vals, 0.99)
    p999 = percentile_from_sorted(finite_vals, 0.999)
    return Stats(n, n_nan, n_inf, mn, mx, mean_v, std_v, p99, p999)


def write_summary(path: Path, rows: list[tuple[FitsImageMeta, Stats]], corr: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "file",
                "naxis1",
                "naxis2",
                "bitpix",
                "ctype1",
                "ctype2",
                "crpix1",
                "crpix2",
                "cdelt1",
                "cdelt2",
                "finite_count",
                "nan_count",
                "inf_count",
                "min",
                "max",
                "mean",
                "stddev",
                "p99",
                "p999",
                "telescope",
            ]
        )
        for meta, st in rows:
            w.writerow(
                [
                    meta.path.name,
                    meta.naxis1,
                    meta.naxis2,
                    meta.bitpix,
                    meta.ctype1,
                    meta.ctype2,
                    meta.crpix1,
                    meta.crpix2,
                    meta.cdelt1,
                    meta.cdelt2,
                    st.finite,
                    st.nan,
                    st.inf,
                    f"{st.min_v:.12g}",
                    f"{st.max_v:.12g}",
                    f"{st.mean_v:.12g}",
                    f"{st.std_v:.12g}",
                    f"{st.p99_v:.12g}",
                    f"{st.p999_v:.12g}",
                    meta.telescope,
                ]
            )
        w.writerow([])
        w.writerow(["cross_band_metric", "value"])
        w.writerow(["pearson_corr_finite_pixels", f"{corr:.12g}"])


def pearson_corr(a: array.array, b: array.array) -> float:
    if len(a) != len(b):
        return float("nan")
    n = 0
    sa = sb = saa = sbb = sab = 0.0
    for va, vb in zip(a, b):
        if not (math.isfinite(va) and math.isfinite(vb)):
            continue
        x = float(va)
        y = float(vb)
        n += 1
        sa += x
        sb += y
        saa += x * x
        sbb += y * y
        sab += x * y
    if n < 3:
        return float("nan")
    ma = sa / n
    mb = sb / n
    va = max(0.0, saa / n - ma * ma)
    vb = max(0.0, sbb / n - mb * mb)
    if va <= 0.0 or vb <= 0.0:
        return float("nan")
    return (sab / n - ma * mb) / math.sqrt(va * vb)


def write_report(path: Path, rows: list[tuple[FitsImageMeta, Stats]], corr: float) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: list[str] = [
        "# DS-006 Assessment - eROSITA TM8 Rates Maps",
        "",
        f"- Generated (UTC): {generated}",
        "",
        "## Files",
        "",
    ]
    for meta, st in rows:
        finite_ratio = st.finite / (meta.naxis1 * meta.naxis2)
        lines += [
            f"### {meta.path.name}",
            "",
            f"- Path: `{meta.path}`",
            f"- Dimensions: `{meta.naxis1} x {meta.naxis2}`",
            f"- Projection: `{meta.ctype1}`, `{meta.ctype2}`",
            f"- Pixel scale: `{meta.cdelt1}` deg/pix, `{meta.cdelt2}` deg/pix",
            f"- Telescope tag: `{meta.telescope}`",
            f"- Finite pixels: `{st.finite}` ({finite_ratio:.3%})",
            f"- NaN pixels: `{st.nan}`",
            f"- Value range: `{st.min_v:.6g}` .. `{st.max_v:.6g}`",
            f"- Mean / std: `{st.mean_v:.6g}` / `{st.std_v:.6g}`",
            "",
        ]

    lines += [
        "## Cross-Band Check",
        "",
        f"- Pearson correlation (finite-pixel overlap): `{corr:.6f}`",
        "",
        "## DS-006 Relevance",
        "",
        "- These maps are valuable as all-sky X-ray plasma intensity layers (baryonic tracer).",
        "- They do not directly provide per-cluster baryon-center vs lensing-center offset pairs.",
        "- They can support DS-006 as an auxiliary X-ray map source, but are not sufficient alone to unlock `gold`.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inspect two eROSITA TM8 FITS rates maps for DS-006.")
    p.add_argument("--file-a", default=str(DEFAULT_LOW), help="First FITS rates map path.")
    p.add_argument("--file-b", default=str(DEFAULT_MID), help="Second FITS rates map path.")
    p.add_argument("--summary-out", default=str(DEFAULT_SUMMARY), help="Summary CSV output path.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT), help="Assessment markdown output path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    fa = Path(args.file_a)
    fb = Path(args.file_b)
    if not fa.exists():
        raise FileNotFoundError(f"Missing file-a: {fa}")
    if not fb.exists():
        raise FileNotFoundError(f"Missing file-b: {fb}")

    meta_a = inspect_primary_image(fa)
    meta_b = inspect_primary_image(fb)

    img_a = load_float_image(meta_a)
    img_b = load_float_image(meta_b)
    stats_a = compute_stats(img_a)
    stats_b = compute_stats(img_b)
    corr = pearson_corr(img_a, img_b)

    summary_out = Path(args.summary_out)
    if not summary_out.is_absolute():
        summary_out = (ROOT / summary_out).resolve()
    report_out = Path(args.report_out)
    if not report_out.is_absolute():
        report_out = (ROOT / report_out).resolve()

    rows = [(meta_a, stats_a), (meta_b, stats_b)]
    write_summary(summary_out, rows, corr)
    write_report(report_out, rows, corr)

    print(f"Summary: {summary_out}")
    print(f"Report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
