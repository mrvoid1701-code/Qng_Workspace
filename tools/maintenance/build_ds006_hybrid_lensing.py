#!/usr/bin/env python3
"""
Build a DS-006 hybrid lensing CSV by combining:
- existing Planck-nlkk proxy rows
- direct literature anchors from Clowe 2006 (Bullet Cluster)
- local eROSITA rates-map gradients sampled at baryonic positions

Outputs:
- data/lensing/lensing_ds006_hybrid.csv
- 05_validation/evidence/artifacts/ds006-hybrid-lensing-build.md
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
DEFAULT_PROXY = ROOT / "data" / "lensing" / "lensing_ds006_planck_proxy.csv"
DEFAULT_CLOWE = ROOT / "data" / "lensing" / "clowe_2006_table2_positions.csv"
DEFAULT_LOW = Path.home() / "Downloads" / "e01_TM8_0.200_0.400keV_3arcm_c947_AIT_sum_Ratesmap.fits"
DEFAULT_MID = Path.home() / "Downloads" / "e01_TM8_0.400_0.600keV_3arcm_c947_AIT_sum_Ratesmap.fits"
DEFAULT_OUT = ROOT / "data" / "lensing" / "lensing_ds006_hybrid.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-hybrid-lensing-build.md"


@dataclass
class MapMeta:
    path: Path
    naxis1: int
    naxis2: int
    cdelt1: float
    cdelt2: float
    crpix1: float
    crpix2: float
    crval1: float
    crval2: float
    data_offset: int
    data_bytes: int


@dataclass
class ClowePair:
    component: str
    ra_bary: float
    dec_bary: float
    ra_lens: float
    dec_lens: float
    mx_bary: float
    mx_lens: float
    k_bary: float
    k_lens: float


def parse_cards(block: bytes) -> list[str]:
    cards: list[str] = []
    for i in range(0, len(block), 80):
        c = block[i : i + 80]
        if len(c) < 80:
            break
        cards.append(c.decode("ascii", errors="replace"))
    return cards


def parse_header(data: bytes, offset: int) -> tuple[dict[str, str], int]:
    out = bytearray()
    off = offset
    while True:
        block = data[off : off + 2880]
        if len(block) < 2880:
            raise RuntimeError("Unexpected EOF in FITS header.")
        out.extend(block)
        off += 2880
        if any(card.startswith("END") for card in parse_cards(block)):
            break
    kv: dict[str, str] = {}
    for card in parse_cards(bytes(out)):
        key = card[:8].strip()
        if not key or key == "END":
            continue
        if card[8:10] == "= ":
            kv[key] = card[10:80].split("/")[0].strip().strip("'")
    return kv, off


def inspect_map(path: Path) -> MapMeta:
    raw = path.read_bytes()
    hdr, off = parse_header(raw, 0)
    n1 = int(hdr.get("NAXIS1", "0"))
    n2 = int(hdr.get("NAXIS2", "0"))
    bitpix = int(hdr.get("BITPIX", "0"))
    if int(hdr.get("NAXIS", "0")) != 2:
        raise RuntimeError(f"{path.name}: expected 2D primary image.")
    data_bytes = n1 * n2 * abs(bitpix) // 8
    return MapMeta(
        path=path,
        naxis1=n1,
        naxis2=n2,
        cdelt1=float(hdr.get("CDELT1", "nan")),
        cdelt2=float(hdr.get("CDELT2", "nan")),
        crpix1=float(hdr.get("CRPIX1", "nan")),
        crpix2=float(hdr.get("CRPIX2", "nan")),
        crval1=float(hdr.get("CRVAL1", "0")),
        crval2=float(hdr.get("CRVAL2", "0")),
        data_offset=off,
        data_bytes=data_bytes,
    )


def load_map(meta: MapMeta) -> array.array:
    raw = meta.path.read_bytes()
    payload = raw[meta.data_offset : meta.data_offset + meta.data_bytes]
    arr = array.array("f")
    arr.frombytes(payload)
    # FITS stores big-endian; x86 is little-endian.
    arr.byteswap()
    return arr


def idx(meta: MapMeta, x: int, y: int) -> int:
    return y * meta.naxis1 + x


def get_pixel(meta: MapMeta, img: array.array, x: int, y: int) -> float:
    if x < 0 or y < 0 or x >= meta.naxis1 or y >= meta.naxis2:
        return float("nan")
    v = float(img[idx(meta, x, y)])
    return v if math.isfinite(v) else float("nan")


def ra_dec_to_gal(ra_deg: float, dec_deg: float) -> tuple[float, float]:
    # J2000 -> Galactic (IAU 1958 / standard constants)
    ra_gp = math.radians(192.85948)
    dec_gp = math.radians(27.12825)
    l_omega = math.radians(32.93192)

    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)

    sin_b = (
        math.sin(dec) * math.sin(dec_gp)
        + math.cos(dec) * math.cos(dec_gp) * math.cos(ra - ra_gp)
    )
    b = math.asin(max(-1.0, min(1.0, sin_b)))

    y = math.cos(dec) * math.sin(ra - ra_gp)
    x = (
        math.sin(dec) * math.cos(dec_gp)
        - math.cos(dec) * math.sin(dec_gp) * math.cos(ra - ra_gp)
    )
    l = l_omega + math.atan2(y, x)
    l = (math.degrees(l) + 360.0) % 360.0
    b_deg = math.degrees(b)
    return l, b_deg


def gal_to_ait_pixel(meta: MapMeta, glon_deg: float, glat_deg: float) -> tuple[float, float]:
    # Hammer-Aitoff forward projection (FITS AIT)
    phi = ((glon_deg - meta.crval1 + 180.0) % 360.0) - 180.0
    theta = glat_deg - meta.crval2
    pr = math.radians(phi)
    tr = math.radians(theta)

    denom = 1.0 + math.cos(tr) * math.cos(pr / 2.0)
    if denom <= 0:
        return float("nan"), float("nan")
    gamma = math.sqrt(2.0 / denom)
    x_rad = 2.0 * gamma * math.cos(tr) * math.sin(pr / 2.0)
    y_rad = gamma * math.sin(tr)
    x_deg = math.degrees(x_rad)
    y_deg = math.degrees(y_rad)

    x_pix = meta.crpix1 + x_deg / meta.cdelt1
    y_pix = meta.crpix2 + y_deg / meta.cdelt2
    return x_pix, y_pix


def local_gradient(meta: MapMeta, img: array.array, x_pix: float, y_pix: float) -> tuple[float, float, float]:
    if not (math.isfinite(x_pix) and math.isfinite(y_pix)):
        return 0.0, 0.0, float("nan")

    x = int(round(x_pix))
    y = int(round(y_pix))
    c = get_pixel(meta, img, x, y)
    if not math.isfinite(c):
        # Try nearest finite in a small window.
        found = False
        for r in range(1, 5):
            for yy in range(y - r, y + r + 1):
                for xx in range(x - r, x + r + 1):
                    v = get_pixel(meta, img, xx, yy)
                    if math.isfinite(v):
                        x, y, c = xx, yy, v
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            return 0.0, 0.0, float("nan")

    l = get_pixel(meta, img, x - 1, y)
    r = get_pixel(meta, img, x + 1, y)
    d = get_pixel(meta, img, x, y - 1)
    u = get_pixel(meta, img, x, y + 1)
    if not math.isfinite(l):
        l = c
    if not math.isfinite(r):
        r = c
    if not math.isfinite(d):
        d = c
    if not math.isfinite(u):
        u = c

    gx = (r - l) / max(2.0 * abs(meta.cdelt1), 1e-12)
    gy = (u - d) / max(2.0 * abs(meta.cdelt2), 1e-12)
    return gx, gy, c


def parse_clowe_pairs(path: Path) -> list[ClowePair]:
    by_component: dict[str, dict[str, dict[str, str]]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            comp = (row.get("component") or "").strip()
            role = (row.get("role") or "").strip().lower()
            if not comp or role not in {"bcg", "plasma"}:
                continue
            by_component.setdefault(comp, {})[role] = row

    out: list[ClowePair] = []
    for comp, roles in by_component.items():
        if "bcg" not in roles or "plasma" not in roles:
            continue
        bcg = roles["bcg"]
        plasma = roles["plasma"]
        out.append(
            ClowePair(
                component=comp,
                ra_bary=float(plasma["ra_deg"]),
                dec_bary=float(plasma["dec_deg"]),
                ra_lens=float(bcg["ra_deg"]),
                dec_lens=float(bcg["dec_deg"]),
                mx_bary=float(plasma["mx_1e12_msun"]),
                mx_lens=float(bcg["mx_1e12_msun"]),
                k_bary=float(plasma["kbar"]),
                k_lens=float(bcg["kbar"]),
            )
        )
    return sorted(out, key=lambda x: x.component)


def build_rows(
    proxy_csv: Path,
    clowe_pairs: list[ClowePair],
    low_meta: MapMeta,
    low_img: array.array,
    mid_meta: MapMeta,
    mid_img: array.array,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    out_rows: list[dict[str, str]] = []
    added_rows: list[dict[str, str]] = []

    with proxy_csv.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            out_rows.append(
                {
                    "system_id": row.get("system_id", ""),
                    "ell": row.get("ell", ""),
                    "obs_dx": row.get("obs_dx", ""),
                    "obs_dy": row.get("obs_dy", ""),
                    "sigma_grad_x": row.get("sigma_grad_x", ""),
                    "sigma_grad_y": row.get("sigma_grad_y", ""),
                    "sigma": row.get("sigma", ""),
                    "mv_nlkk": row.get("mv_nlkk", ""),
                    "pp_nlkk": row.get("pp_nlkk", ""),
                    "source_tag": "planck_proxy",
                    "source_ref": "COM_Lensing_4096_R3.00 MV/PP nlkk (proxy)",
                    "ra_bary_deg": "",
                    "dec_bary_deg": "",
                    "ra_lens_deg": "",
                    "dec_lens_deg": "",
                    "glon_bary_deg": "",
                    "glat_bary_deg": "",
                    "ratesmap_low": "",
                    "ratesmap_mid": "",
                }
            )

    for pair in clowe_pairs:
        obs_dx = (pair.ra_lens - pair.ra_bary) * math.cos(math.radians(pair.dec_bary)) * 60.0
        obs_dy = (pair.dec_lens - pair.dec_bary) * 60.0
        glon, glat = ra_dec_to_gal(pair.ra_bary, pair.dec_bary)

        lx, ly = gal_to_ait_pixel(low_meta, glon, glat)
        mx, my = gal_to_ait_pixel(mid_meta, glon, glat)
        gx_l, gy_l, v_l = local_gradient(low_meta, low_img, lx, ly)
        gx_m, gy_m, v_m = local_gradient(mid_meta, mid_img, mx, my)

        gx = 0.5 * (gx_l + gx_m)
        gy = 0.5 * (gy_l + gy_m)
        if not math.isfinite(gx):
            gx = 0.0
        if not math.isfinite(gy):
            gy = 0.0
        # Fallback if maps are locally undefined.
        if abs(gx) + abs(gy) < 1e-12:
            gx = obs_dx
            gy = obs_dy

        row = {
            "system_id": f"CLOWE-{pair.component}",
            "ell": "",
            "obs_dx": f"{obs_dx:.9f}",
            "obs_dy": f"{obs_dy:.9f}",
            "sigma_grad_x": f"{gx:.9f}",
            "sigma_grad_y": f"{gy:.9f}",
            "sigma": "0.300000000",
            "mv_nlkk": "",
            "pp_nlkk": "",
            "source_tag": "clowe2006_direct",
            "source_ref": "Clowe_2006_ApJ_648_L109 Table 2 (BCG vs plasma)",
            "ra_bary_deg": f"{pair.ra_bary:.10f}",
            "dec_bary_deg": f"{pair.dec_bary:.10f}",
            "ra_lens_deg": f"{pair.ra_lens:.10f}",
            "dec_lens_deg": f"{pair.dec_lens:.10f}",
            "glon_bary_deg": f"{glon:.10f}",
            "glat_bary_deg": f"{glat:.10f}",
            "ratesmap_low": f"{v_l:.9g}" if math.isfinite(v_l) else "",
            "ratesmap_mid": f"{v_m:.9g}" if math.isfinite(v_m) else "",
        }
        out_rows.append(row)
        added_rows.append(row)

    return out_rows, added_rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "system_id",
        "ell",
        "obs_dx",
        "obs_dy",
        "sigma_grad_x",
        "sigma_grad_y",
        "sigma",
        "mv_nlkk",
        "pp_nlkk",
        "source_tag",
        "source_ref",
        "ra_bary_deg",
        "dec_bary_deg",
        "ra_lens_deg",
        "dec_lens_deg",
        "glon_bary_deg",
        "glat_bary_deg",
        "ratesmap_low",
        "ratesmap_mid",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_report(path: Path, out_csv: Path, total_rows: int, added_rows: list[dict[str, str]]) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# DS-006 Hybrid Lensing Build",
        "",
        f"- Generated (UTC): {generated}",
        f"- Output CSV: `{out_csv}`",
        f"- Total rows: `{total_rows}`",
        f"- Added direct rows: `{len(added_rows)}`",
        "",
        "## Added Rows (Clowe 2006 Anchors)",
        "",
        "| system_id | obs_dx (arcmin) | obs_dy (arcmin) | sigma_grad_x | sigma_grad_y | glon | glat |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in added_rows:
        lines.append(
            f"| {row['system_id']} | {row['obs_dx']} | {row['obs_dy']} | "
            f"{row['sigma_grad_x']} | {row['sigma_grad_y']} | {row['glon_bary_deg']} | {row['glat_bary_deg']} |"
        )
    lines += [
        "",
        "Interpretation:",
        "- This hybrid file keeps all proxy rows and appends direct literature anchors.",
        "- It improves external anchoring but does not replace the need for a larger direct multi-cluster offset catalog.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build DS-006 hybrid lensing CSV.")
    p.add_argument("--proxy-csv", default=str(DEFAULT_PROXY), help="Existing proxy lensing CSV.")
    p.add_argument("--clowe-csv", default=str(DEFAULT_CLOWE), help="Parsed Clowe Table-2 CSV.")
    p.add_argument("--ratesmap-low", default=str(DEFAULT_LOW), help="eROSITA 0.2-0.4 keV FITS.")
    p.add_argument("--ratesmap-mid", default=str(DEFAULT_MID), help="eROSITA 0.4-0.6 keV FITS.")
    p.add_argument("--out-csv", default=str(DEFAULT_OUT), help="Hybrid output CSV.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT), help="Build report markdown path.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    proxy = Path(args.proxy_csv)
    clowe = Path(args.clowe_csv)
    low = Path(args.ratesmap_low)
    mid = Path(args.ratesmap_mid)
    out_csv = Path(args.out_csv)
    report = Path(args.report_out)

    if not proxy.exists():
        raise FileNotFoundError(f"Proxy CSV not found: {proxy}")
    if not clowe.exists():
        raise FileNotFoundError(f"Clowe CSV not found: {clowe}")
    if not low.exists():
        raise FileNotFoundError(f"Ratesmap-low not found: {low}")
    if not mid.exists():
        raise FileNotFoundError(f"Ratesmap-mid not found: {mid}")

    if not out_csv.is_absolute():
        out_csv = (ROOT / out_csv).resolve()
    if not report.is_absolute():
        report = (ROOT / report).resolve()

    clowe_pairs = parse_clowe_pairs(clowe)
    if not clowe_pairs:
        raise RuntimeError("No usable Clowe pairs were parsed.")

    low_meta = inspect_map(low)
    mid_meta = inspect_map(mid)
    low_img = load_map(low_meta)
    mid_img = load_map(mid_meta)

    rows, added = build_rows(proxy, clowe_pairs, low_meta, low_img, mid_meta, mid_img)
    write_rows(out_csv, rows)
    write_report(report, out_csv, len(rows), added)

    print(f"Hybrid rows: {len(rows)} (added direct rows: {len(added)})")
    print(f"Output: {out_csv}")
    print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
