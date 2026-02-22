#!/usr/bin/env python3
"""
Build a DS-006 cluster-offset CSV from local baryon/lensing catalogs.

This script is intentionally stdlib-only and supports two input modes:
1) Two-catalog mode:
   - --baryon-csv (X-ray / baryonic centers)
   - --lensing-csv (lensing centers)
2) Combined-catalog mode:
   - --combined-csv with role split (e.g. role=plasma vs role=bcg)

Output schema is compatible with scripts/run_qng_t_027_lensing_dark.py:
- baryon_x/baryon_y/lens_x/lens_y
- sigma_grad_x/sigma_grad_y
- sigma
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import math
import statistics


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "lensing" / "cluster_offsets_real.csv"
DEFAULT_REPORT = ROOT / "05_validation" / "evidence" / "artifacts" / "ds006-cluster-offset-build.md"
DEFAULT_UNMATCHED_B = ROOT / "data" / "lensing" / "cluster_offsets_unmatched_baryon.csv"
DEFAULT_UNMATCHED_L = ROOT / "data" / "lensing" / "cluster_offsets_unmatched_lensing.csv"


@dataclass
class CatalogRow:
    row_idx: int
    raw_id: str
    norm_id: str
    ra_deg: float
    dec_deg: float
    grad_x: float | None
    grad_y: float | None
    sigma: float | None
    source_tag: str


@dataclass
class Match:
    baryon_idx: int
    lens_idx: int
    sep_arcmin: float
    mode: str


ID_ALIASES = [
    "system_id",
    "cluster_id",
    "id",
    "name",
    "cluster",
    "objname",
    "object",
    "component",
]
RA_ALIASES = ["ra_deg", "ra", "ra_icrs", "ra_j2000", "ra2000"]
DEC_ALIASES = ["dec_deg", "dec", "dec_icrs", "dec_j2000", "de2000", "dec2000"]
GRAD_X_ALIASES = ["sigma_grad_x", "grad_x", "history_dx", "memory_dx"]
GRAD_Y_ALIASES = ["sigma_grad_y", "grad_y", "history_dy", "memory_dy"]
SIGMA_ALIASES = ["sigma", "offset_err", "error", "err"]
ROLE_ALIASES = ["role", "type", "class", "kind"]


def safe_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_header_map(fieldnames: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in fieldnames or []:
        out[name.lower().strip()] = name
    return out


def pick_col(hmap: dict[str, str], aliases: list[str], explicit: str = "") -> str | None:
    if explicit:
        key = explicit.lower().strip()
        if key in hmap:
            return hmap[key]
        return None
    for alias in aliases:
        key = alias.lower().strip()
        if key in hmap:
            return hmap[key]
    return None


def normalize_id(value: str) -> str:
    text = "".join(ch for ch in value.upper() if ch.isalnum())
    return text


def resolve_path(path_arg: str) -> Path:
    p = Path(path_arg)
    if p.is_absolute():
        return p
    return (ROOT / p).resolve()


def angular_sep_arcmin(ra1_deg: float, dec1_deg: float, ra2_deg: float, dec2_deg: float) -> float:
    ra1 = math.radians(ra1_deg)
    dec1 = math.radians(dec1_deg)
    ra2 = math.radians(ra2_deg)
    dec2 = math.radians(dec2_deg)

    d_ra = ra2 - ra1
    d_dec = dec2 - dec1
    a = math.sin(d_dec / 2.0) ** 2 + math.cos(dec1) * math.cos(dec2) * math.sin(d_ra / 2.0) ** 2
    c = 2.0 * math.asin(min(1.0, math.sqrt(max(0.0, a))))
    return math.degrees(c) * 60.0


def delta_ra_wrapped_deg(ra2_deg: float, ra1_deg: float) -> float:
    d = ra2_deg - ra1_deg
    while d > 180.0:
        d -= 360.0
    while d < -180.0:
        d += 360.0
    return d


def parse_catalog(
    *,
    csv_path: Path,
    source_tag: str,
    id_col: str,
    ra_col: str,
    dec_col: str,
    grad_x_col: str,
    grad_y_col: str,
    sigma_col: str,
    role_col: str,
    role_value: str,
    group_col: str,
) -> tuple[list[CatalogRow], dict[str, str], list[str]]:
    rows: list[CatalogRow] = []
    warnings: list[str] = []

    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        hmap = normalize_header_map(reader.fieldnames)

        c_role = pick_col(hmap, ROLE_ALIASES, explicit=role_col) if role_value else None
        c_id = pick_col(hmap, ID_ALIASES, explicit=(group_col or id_col))
        c_ra = pick_col(hmap, RA_ALIASES, explicit=ra_col)
        c_dec = pick_col(hmap, DEC_ALIASES, explicit=dec_col)
        c_gx = pick_col(hmap, GRAD_X_ALIASES, explicit=grad_x_col)
        c_gy = pick_col(hmap, GRAD_Y_ALIASES, explicit=grad_y_col)
        c_sigma = pick_col(hmap, SIGMA_ALIASES, explicit=sigma_col)

        if c_ra is None or c_dec is None:
            raise ValueError(
                f"{csv_path}: missing RA/Dec columns. "
                f"Use --ra-col-* and --dec-col-* to map your schema."
            )

        resolved_cols = {
            "id": c_id or "",
            "ra": c_ra,
            "dec": c_dec,
            "grad_x": c_gx or "",
            "grad_y": c_gy or "",
            "sigma": c_sigma or "",
            "role": c_role or "",
        }

        role_target = role_value.lower().strip()
        for i, row in enumerate(reader, start=1):
            if c_role and role_target:
                role_now = str(row.get(c_role, "")).strip().lower()
                if role_now != role_target:
                    continue

            ra = safe_float(row.get(c_ra))
            dec = safe_float(row.get(c_dec))
            if ra is None or dec is None:
                warnings.append(f"{csv_path.name} row {i}: skipped (invalid ra/dec)")
                continue

            raw_id = ""
            if c_id:
                raw_id = str(row.get(c_id, "")).strip()
            if not raw_id:
                raw_id = f"{source_tag}-{i}"

            gx = safe_float(row.get(c_gx)) if c_gx else None
            gy = safe_float(row.get(c_gy)) if c_gy else None
            sigma = safe_float(row.get(c_sigma)) if c_sigma else None

            rows.append(
                CatalogRow(
                    row_idx=i,
                    raw_id=raw_id,
                    norm_id=normalize_id(raw_id),
                    ra_deg=float(ra),
                    dec_deg=float(dec),
                    grad_x=gx,
                    grad_y=gy,
                    sigma=sigma if (sigma is not None and sigma > 0) else None,
                    source_tag=source_tag,
                )
            )

    return rows, resolved_cols, warnings


def match_rows(
    baryon_rows: list[CatalogRow],
    lens_rows: list[CatalogRow],
    match_mode: str,
    min_sep_arcmin: float,
    max_sep_arcmin: float,
    strict_id_sep: bool,
) -> tuple[list[Match], list[int], list[int], list[str]]:
    warnings: list[str] = []
    matches: list[Match] = []

    unmatched_b = set(range(len(baryon_rows)))
    unmatched_l = set(range(len(lens_rows)))

    def sep(bi: int, li: int) -> float:
        b = baryon_rows[bi]
        l = lens_rows[li]
        return angular_sep_arcmin(b.ra_deg, b.dec_deg, l.ra_deg, l.dec_deg)

    if match_mode in {"id", "hybrid"}:
        lens_by_id: dict[str, list[int]] = {}
        for li, row in enumerate(lens_rows):
            if row.norm_id:
                lens_by_id.setdefault(row.norm_id, []).append(li)

        for bi, b in enumerate(baryon_rows):
            if bi not in unmatched_b or not b.norm_id:
                continue
            candidates = [li for li in lens_by_id.get(b.norm_id, []) if li in unmatched_l]
            if not candidates:
                continue
            if len(candidates) == 1:
                li_best = candidates[0]
            else:
                li_best = min(candidates, key=lambda li: sep(bi, li))
            d = sep(bi, li_best)
            if d > max_sep_arcmin:
                if strict_id_sep:
                    warnings.append(
                        f"ID match '{b.raw_id}' dropped: separation {d:.3f} arcmin (> {max_sep_arcmin:.3f})."
                    )
                    continue
                warnings.append(
                    f"ID match '{b.raw_id}' has large separation {d:.3f} arcmin (> {max_sep_arcmin:.3f})."
                )
            matches.append(Match(baryon_idx=bi, lens_idx=li_best, sep_arcmin=d, mode="id"))
            unmatched_b.discard(bi)
            unmatched_l.discard(li_best)

    if match_mode in {"sky", "hybrid"} and unmatched_b and unmatched_l:
        candidates: list[tuple[float, int, int]] = []
        for bi in unmatched_b:
            for li in unmatched_l:
                d = sep(bi, li)
                if min_sep_arcmin <= d <= max_sep_arcmin:
                    candidates.append((d, bi, li))

        candidates.sort(key=lambda x: x[0])
        used_b: set[int] = set()
        used_l: set[int] = set()
        for d, bi, li in candidates:
            if bi in used_b or li in used_l:
                continue
            matches.append(Match(baryon_idx=bi, lens_idx=li, sep_arcmin=d, mode="sky"))
            used_b.add(bi)
            used_l.add(li)

        unmatched_b -= used_b
        unmatched_l -= used_l

    matches.sort(key=lambda m: (m.sep_arcmin, m.baryon_idx, m.lens_idx))
    return matches, sorted(unmatched_b), sorted(unmatched_l), warnings


def build_offset_rows(
    matches: list[Match],
    baryon_rows: list[CatalogRow],
    lens_rows: list[CatalogRow],
    default_sigma: float,
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    for i, m in enumerate(matches, start=1):
        b = baryon_rows[m.baryon_idx]
        l = lens_rows[m.lens_idx]

        d_ra = delta_ra_wrapped_deg(l.ra_deg, b.ra_deg)
        dx_arcmin = d_ra * math.cos(math.radians(b.dec_deg)) * 60.0
        dy_arcmin = (l.dec_deg - b.dec_deg) * 60.0

        gx = l.grad_x if l.grad_x is not None else dx_arcmin
        gy = l.grad_y if l.grad_y is not None else dy_arcmin
        sigma = l.sigma if l.sigma is not None else max(default_sigma, 1e-6)

        if b.norm_id and b.norm_id == l.norm_id:
            sid = b.raw_id
        elif b.raw_id and l.raw_id:
            sid = f"{b.raw_id}__{l.raw_id}"
        else:
            sid = f"CL-{i:05d}"

        out.append(
            {
                "system_id": sid,
                "baryon_x": "0.000000000",
                "baryon_y": "0.000000000",
                "lens_x": f"{dx_arcmin:.9f}",
                "lens_y": f"{dy_arcmin:.9f}",
                "sigma_grad_x": f"{gx:.9f}",
                "sigma_grad_y": f"{gy:.9f}",
                "sigma": f"{sigma:.9f}",
                "baryon_ra_deg": f"{b.ra_deg:.10f}",
                "baryon_dec_deg": f"{b.dec_deg:.10f}",
                "lens_ra_deg": f"{l.ra_deg:.10f}",
                "lens_dec_deg": f"{l.dec_deg:.10f}",
                "sep_arcmin": f"{m.sep_arcmin:.9f}",
                "match_mode": m.mode,
                "baryon_id": b.raw_id,
                "lens_id": l.raw_id,
                "baryon_source": b.source_tag,
                "lens_source": l.source_tag,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_unmatched(path: Path, rows: list[CatalogRow], indices: list[int], side: str) -> None:
    fields = ["side", "raw_id", "norm_id", "ra_deg", "dec_deg", "source_tag", "row_idx"]
    out_rows: list[dict[str, str]] = []
    for idx in indices:
        r = rows[idx]
        out_rows.append(
            {
                "side": side,
                "raw_id": r.raw_id,
                "norm_id": r.norm_id,
                "ra_deg": f"{r.ra_deg:.10f}",
                "dec_deg": f"{r.dec_deg:.10f}",
                "source_tag": r.source_tag,
                "row_idx": str(r.row_idx),
            }
        )
    write_csv(path, out_rows, fields)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    s = sorted(values)
    pos = (len(s) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    frac = pos - lo
    return s[lo] * (1.0 - frac) + s[hi] * frac


def write_report(
    path: Path,
    *,
    input_mode: str,
    baryon_csv: Path | None,
    lensing_csv: Path | None,
    combined_csv: Path | None,
    out_csv: Path,
    unmatched_b_csv: Path,
    unmatched_l_csv: Path,
    matches: list[Match],
    unmatched_b: list[int],
    unmatched_l: list[int],
    baryon_rows: list[CatalogRow],
    lens_rows: list[CatalogRow],
    min_sep_arcmin: float,
    max_sep_arcmin: float,
    match_mode: str,
    strict_id_sep: bool,
    warnings: list[str],
    baryon_cols: dict[str, str],
    lens_cols: dict[str, str],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    sep_values = [m.sep_arcmin for m in matches]
    by_mode: dict[str, int] = {}
    for m in matches:
        by_mode[m.mode] = by_mode.get(m.mode, 0) + 1

    lines: list[str] = [
        "# DS-006 Cluster Offset Build",
        "",
        f"- Generated (UTC): {now}",
        f"- Input mode: `{input_mode}`",
        f"- Match mode: `{match_mode}`",
        f"- Strict ID separation gate: `{strict_id_sep}`",
        f"- Separation window (arcmin): `[{min_sep_arcmin:.3f}, {max_sep_arcmin:.3f}]`",
        "",
        "## Inputs",
        "",
        f"- Baryon CSV: `{baryon_csv}`" if baryon_csv else "- Baryon CSV: `N/A (combined mode)`",
        f"- Lensing CSV: `{lensing_csv}`" if lensing_csv else "- Lensing CSV: `N/A (combined mode)`",
        f"- Combined CSV: `{combined_csv}`" if combined_csv else "- Combined CSV: `N/A`",
        "",
        "## Column Mapping",
        "",
        f"- Baryon: id=`{baryon_cols.get('id', '')}`, ra=`{baryon_cols.get('ra', '')}`, dec=`{baryon_cols.get('dec', '')}`, "
        f"grad_x=`{baryon_cols.get('grad_x', '')}`, grad_y=`{baryon_cols.get('grad_y', '')}`, sigma=`{baryon_cols.get('sigma', '')}`",
        f"- Lensing: id=`{lens_cols.get('id', '')}`, ra=`{lens_cols.get('ra', '')}`, dec=`{lens_cols.get('dec', '')}`, "
        f"grad_x=`{lens_cols.get('grad_x', '')}`, grad_y=`{lens_cols.get('grad_y', '')}`, sigma=`{lens_cols.get('sigma', '')}`",
        "",
        "## Match Summary",
        "",
        f"- Parsed baryon rows: `{len(baryon_rows)}`",
        f"- Parsed lensing rows: `{len(lens_rows)}`",
        f"- Matched rows: `{len(matches)}`",
        f"- Unmatched baryon rows: `{len(unmatched_b)}`",
        f"- Unmatched lensing rows: `{len(unmatched_l)}`",
        f"- Matched by id: `{by_mode.get('id', 0)}`",
        f"- Matched by sky: `{by_mode.get('sky', 0)}`",
        "",
        "## Separation Stats (arcmin)",
        "",
        f"- min: `{min(sep_values):.6f}`" if sep_values else "- min: `nan`",
        f"- median: `{statistics.median(sep_values):.6f}`" if sep_values else "- median: `nan`",
        f"- p90: `{percentile(sep_values, 0.90):.6f}`" if sep_values else "- p90: `nan`",
        f"- max: `{max(sep_values):.6f}`" if sep_values else "- max: `nan`",
        "",
        "## Outputs",
        "",
        f"- Cluster offsets CSV: `{out_csv}`",
        f"- Unmatched baryon CSV: `{unmatched_b_csv}`",
        f"- Unmatched lensing CSV: `{unmatched_l_csv}`",
        "",
        "## Warnings",
        "",
    ]

    if warnings:
        for w in warnings[:30]:
            lines.append(f"- {w}")
        if len(warnings) > 30:
            lines.append(f"- ... ({len(warnings) - 30} more)")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Next Step",
        "",
        "Run DS-006 strict input on this catalog:",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe scripts\\run_qng_t_027_lensing_dark.py `",
        "  --dataset-id DS-006 `",
        "  --model-baseline gr_dm `",
        "  --model-memory qng_sigma_memory `",
        f"  --lensing-csv \"{out_csv}\" `",
        "  --rotation-csv \"data/rotation/rotation_ds006_rotmod.csv\" `",
        "  --out-dir \"05_validation/evidence/artifacts/qng-t-027\" `",
        "  --seed 42 `",
        "  --strict-input",
        "```",
        "",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build DS-006 cluster offset catalog from local CSV files.")
    p.add_argument("--baryon-csv", default="", help="Baryonic-center catalog CSV.")
    p.add_argument("--lensing-csv", default="", help="Lensing-center catalog CSV.")
    p.add_argument("--combined-csv", default="", help="Single CSV with both roles (e.g. plasma vs bcg).")

    p.add_argument("--id-col-baryon", default="", help="Baryon ID column override.")
    p.add_argument("--id-col-lensing", default="", help="Lensing ID column override.")
    p.add_argument("--ra-col-baryon", default="", help="Baryon RA column override.")
    p.add_argument("--dec-col-baryon", default="", help="Baryon Dec column override.")
    p.add_argument("--ra-col-lensing", default="", help="Lensing RA column override.")
    p.add_argument("--dec-col-lensing", default="", help="Lensing Dec column override.")
    p.add_argument("--grad-x-col-lensing", default="", help="Lensing grad-x column override.")
    p.add_argument("--grad-y-col-lensing", default="", help="Lensing grad-y column override.")
    p.add_argument("--sigma-col-lensing", default="", help="Lensing sigma column override.")

    p.add_argument("--role-col", default="", help="Role column for --combined-csv.")
    p.add_argument("--group-col", default="", help="Group/cluster column for --combined-csv.")
    p.add_argument("--baryon-role", default="plasma", help="Role value used as baryonic center.")
    p.add_argument("--lensing-role", default="bcg", help="Role value used as lensing center.")

    p.add_argument("--match-mode", choices=["id", "sky", "hybrid"], default="hybrid", help="Matching strategy.")
    p.add_argument("--min-sep-arcmin", type=float, default=0.0, help="Minimum allowed sky separation.")
    p.add_argument("--max-sep-arcmin", type=float, default=5.0, help="Maximum allowed sky separation.")
    p.add_argument(
        "--strict-id-sep",
        action="store_true",
        help="Drop ID matches whose sky separation exceeds --max-sep-arcmin.",
    )
    p.add_argument("--default-sigma", type=float, default=0.30, help="Fallback sigma value if missing.")

    p.add_argument("--out-csv", default=str(DEFAULT_OUT), help="Output cluster-offset CSV path.")
    p.add_argument("--report-out", default=str(DEFAULT_REPORT), help="Output markdown report path.")
    p.add_argument(
        "--out-unmatched-baryon",
        default=str(DEFAULT_UNMATCHED_B),
        help="CSV path for unmatched baryon rows.",
    )
    p.add_argument(
        "--out-unmatched-lensing",
        default=str(DEFAULT_UNMATCHED_L),
        help="CSV path for unmatched lensing rows.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    out_csv = resolve_path(args.out_csv)
    report_out = resolve_path(args.report_out)
    out_unmatched_b = resolve_path(args.out_unmatched_baryon)
    out_unmatched_l = resolve_path(args.out_unmatched_lensing)

    if args.min_sep_arcmin < 0:
        raise ValueError("--min-sep-arcmin must be >= 0")
    if args.max_sep_arcmin <= 0:
        raise ValueError("--max-sep-arcmin must be > 0")
    if args.min_sep_arcmin > args.max_sep_arcmin:
        raise ValueError("--min-sep-arcmin cannot exceed --max-sep-arcmin")

    baryon_rows: list[CatalogRow]
    lens_rows: list[CatalogRow]
    baryon_cols: dict[str, str]
    lens_cols: dict[str, str]
    warnings: list[str] = []
    input_mode = ""
    baryon_csv_path: Path | None = None
    lensing_csv_path: Path | None = None
    combined_csv_path: Path | None = None

    if args.combined_csv:
        combined_csv_path = resolve_path(args.combined_csv)
        if not combined_csv_path.exists():
            raise FileNotFoundError(f"Combined CSV not found: {combined_csv_path}")
        input_mode = "combined"

        baryon_rows, baryon_cols, w_b = parse_catalog(
            csv_path=combined_csv_path,
            source_tag=f"{combined_csv_path.name}:{args.baryon_role}",
            id_col=args.id_col_baryon,
            ra_col=args.ra_col_baryon,
            dec_col=args.dec_col_baryon,
            grad_x_col="",
            grad_y_col="",
            sigma_col="",
            role_col=args.role_col,
            role_value=args.baryon_role,
            group_col=args.group_col,
        )
        lens_rows, lens_cols, w_l = parse_catalog(
            csv_path=combined_csv_path,
            source_tag=f"{combined_csv_path.name}:{args.lensing_role}",
            id_col=args.id_col_lensing,
            ra_col=args.ra_col_lensing,
            dec_col=args.dec_col_lensing,
            grad_x_col=args.grad_x_col_lensing,
            grad_y_col=args.grad_y_col_lensing,
            sigma_col=args.sigma_col_lensing,
            role_col=args.role_col,
            role_value=args.lensing_role,
            group_col=args.group_col,
        )
        warnings.extend(w_b)
        warnings.extend(w_l)
    else:
        if not args.baryon_csv or not args.lensing_csv:
            raise ValueError("Provide --baryon-csv and --lensing-csv, or use --combined-csv.")
        baryon_csv_path = resolve_path(args.baryon_csv)
        lensing_csv_path = resolve_path(args.lensing_csv)
        if not baryon_csv_path.exists():
            raise FileNotFoundError(f"Baryon CSV not found: {baryon_csv_path}")
        if not lensing_csv_path.exists():
            raise FileNotFoundError(f"Lensing CSV not found: {lensing_csv_path}")
        input_mode = "two-catalog"

        baryon_rows, baryon_cols, w_b = parse_catalog(
            csv_path=baryon_csv_path,
            source_tag=baryon_csv_path.name,
            id_col=args.id_col_baryon,
            ra_col=args.ra_col_baryon,
            dec_col=args.dec_col_baryon,
            grad_x_col="",
            grad_y_col="",
            sigma_col="",
            role_col="",
            role_value="",
            group_col="",
        )
        lens_rows, lens_cols, w_l = parse_catalog(
            csv_path=lensing_csv_path,
            source_tag=lensing_csv_path.name,
            id_col=args.id_col_lensing,
            ra_col=args.ra_col_lensing,
            dec_col=args.dec_col_lensing,
            grad_x_col=args.grad_x_col_lensing,
            grad_y_col=args.grad_y_col_lensing,
            sigma_col=args.sigma_col_lensing,
            role_col="",
            role_value="",
            group_col="",
        )
        warnings.extend(w_b)
        warnings.extend(w_l)

    if not baryon_rows:
        raise RuntimeError("No usable baryon rows parsed.")
    if not lens_rows:
        raise RuntimeError("No usable lensing rows parsed.")

    matches, unmatched_b, unmatched_l, w_match = match_rows(
        baryon_rows=baryon_rows,
        lens_rows=lens_rows,
        match_mode=args.match_mode,
        min_sep_arcmin=args.min_sep_arcmin,
        max_sep_arcmin=args.max_sep_arcmin,
        strict_id_sep=args.strict_id_sep,
    )
    warnings.extend(w_match)

    if not matches:
        raise RuntimeError("No matched rows found. Adjust column mapping or separation threshold.")

    out_rows = build_offset_rows(matches, baryon_rows, lens_rows, default_sigma=max(args.default_sigma, 1e-6))
    out_fields = [
        "system_id",
        "baryon_x",
        "baryon_y",
        "lens_x",
        "lens_y",
        "sigma_grad_x",
        "sigma_grad_y",
        "sigma",
        "baryon_ra_deg",
        "baryon_dec_deg",
        "lens_ra_deg",
        "lens_dec_deg",
        "sep_arcmin",
        "match_mode",
        "baryon_id",
        "lens_id",
        "baryon_source",
        "lens_source",
    ]
    write_csv(out_csv, out_rows, out_fields)
    write_unmatched(out_unmatched_b, baryon_rows, unmatched_b, side="baryon")
    write_unmatched(out_unmatched_l, lens_rows, unmatched_l, side="lensing")

    write_report(
        report_out,
        input_mode=input_mode,
        baryon_csv=baryon_csv_path,
        lensing_csv=lensing_csv_path,
        combined_csv=combined_csv_path,
        out_csv=out_csv,
        unmatched_b_csv=out_unmatched_b,
        unmatched_l_csv=out_unmatched_l,
        matches=matches,
        unmatched_b=unmatched_b,
        unmatched_l=unmatched_l,
        baryon_rows=baryon_rows,
        lens_rows=lens_rows,
        min_sep_arcmin=args.min_sep_arcmin,
        max_sep_arcmin=args.max_sep_arcmin,
        match_mode=args.match_mode,
        strict_id_sep=args.strict_id_sep,
        warnings=warnings,
        baryon_cols=baryon_cols,
        lens_cols=lens_cols,
    )

    by_mode: dict[str, int] = {}
    for m in matches:
        by_mode[m.mode] = by_mode.get(m.mode, 0) + 1
    print(f"Input mode: {input_mode}")
    print(f"Baryon parsed: {len(baryon_rows)} | Lensing parsed: {len(lens_rows)}")
    print(f"Matched rows: {len(matches)} (id={by_mode.get('id', 0)}, sky={by_mode.get('sky', 0)})")
    print(f"Unmatched baryon: {len(unmatched_b)} | Unmatched lensing: {len(unmatched_l)}")
    print(f"Output CSV: {out_csv}")
    print(f"Report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
