#!/usr/bin/env python3
"""
Prepare DS-006 input CSV files from local downloads/extracted assets.

Outputs:
- data/rotation/rotation_ds006_rotmod.csv
- data/lensing/lensing_ds006_planck_proxy.csv

Notes:
- Rotation CSV is built from Rotmod_LTG *.dat files.
- Lensing CSV is built as a reproducible proxy from Planck lensing nlkk tables
  (MV/PP), for workflow execution when cluster map catalogs are not yet present.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import csv
import math
import statistics


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROTMOD_DIR = Path.home() / "Downloads" / "Rotmod_LTG"
PREFERRED_MV_NLKK = (
    ROOT
    / "data"
    / "lensing"
    / "planck_lensing_4096_r3"
    / "COM_Lensing_4096_R3.00"
    / "MV"
    / "nlkk.dat"
)
PREFERRED_PP_NLKK = (
    ROOT
    / "data"
    / "lensing"
    / "planck_lensing_4096_r3"
    / "COM_Lensing_4096_R3.00"
    / "PP"
    / "nlkk.dat"
)
FALLBACK_MV_NLKK = (
    ROOT
    / "data"
    / "lensing"
    / "planck_lensing_4096_r3_part"
    / "COM_Lensing_4096_R3.00"
    / "MV"
    / "nlkk.dat"
)
FALLBACK_PP_NLKK = (
    ROOT
    / "data"
    / "lensing"
    / "planck_lensing_4096_r3_part"
    / "COM_Lensing_4096_R3.00"
    / "PP"
    / "nlkk.dat"
)
DEFAULT_ROT_OUT = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_LENS_OUT = ROOT / "data" / "lensing" / "lensing_ds006_planck_proxy.csv"


def default_nlkk_paths() -> tuple[Path, Path]:
    if PREFERRED_MV_NLKK.exists() and PREFERRED_PP_NLKK.exists():
        return PREFERRED_MV_NLKK, PREFERRED_PP_NLKK
    return FALLBACK_MV_NLKK, FALLBACK_PP_NLKK


@dataclass
class RotRow:
    system_id: str
    radius: float
    v_obs: float
    v_err: float
    baryon_term: float
    history_term: float


def parse_rotmod_file(path: Path) -> list[RotRow]:
    rows: list[RotRow] = []
    sid = path.stem.replace("_rotmod", "")
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split()
        if len(cols) < 6:
            continue
        try:
            radius = float(cols[0])
            v_obs = float(cols[1])
            v_err = abs(float(cols[2]))
            v_gas = float(cols[3])
            v_disk = float(cols[4])
            v_bul = float(cols[5])
        except ValueError:
            continue
        baryon_term = v_gas * v_gas + v_disk * v_disk + v_bul * v_bul
        history_term = max(v_obs * v_obs - baryon_term, 0.0)
        rows.append(
            RotRow(
                system_id=sid,
                radius=radius,
                v_obs=max(v_obs, 1e-6),
                v_err=max(v_err, 1e-6),
                baryon_term=max(baryon_term, 0.0),
                history_term=history_term,
            )
        )
    return rows


def write_rotation_csv(rows: list[RotRow], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows_sorted = sorted(rows, key=lambda r: (r.system_id, r.radius))
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "radius", "v_obs", "v_err", "baryon_term", "history_term"])
        for r in rows_sorted:
            w.writerow(
                [
                    r.system_id,
                    f"{r.radius:.6f}",
                    f"{r.v_obs:.6f}",
                    f"{r.v_err:.6f}",
                    f"{r.baryon_term:.6f}",
                    f"{r.history_term:.6f}",
                ]
            )


def read_nlkk(path: Path) -> dict[int, tuple[float, float]]:
    rows: dict[int, tuple[float, float]] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split()
        if len(cols) < 3:
            continue
        try:
            ell = int(float(cols[0]))
            v1 = float(cols[1])
            v2 = float(cols[2])
        except ValueError:
            continue
        rows[ell] = (v1, v2)
    return rows


def zscore(values: list[float]) -> list[float]:
    if not values:
        return []
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 1.0
    if std_v <= 1e-12:
        std_v = 1.0
    return [(v - mean_v) / std_v for v in values]


def write_lensing_proxy_csv(
    mv_map: dict[int, tuple[float, float]],
    pp_map: dict[int, tuple[float, float]],
    out_path: Path,
    ell_min: int,
    ell_max: int,
    stride: int,
) -> int:
    common = sorted(k for k in set(mv_map) & set(pp_map) if ell_min <= k <= ell_max)
    if stride > 1:
        common = common[::stride]

    mv_vals = [math.log10(max(mv_map[ell][1], 1e-40)) for ell in common]
    pp_vals = [math.log10(max(pp_map[ell][1], 1e-40)) for ell in common]
    mv_z = zscore(mv_vals)
    pp_z = zscore(pp_vals)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "system_id",
                "ell",
                "obs_dx",
                "obs_dy",
                "sigma_grad_x",
                "sigma_grad_y",
                "sigma",
                "mv_nlkk",
                "pp_nlkk",
            ]
        )
        for idx, ell in enumerate(common, start=1):
            gx = mv_z[idx - 1]
            gy = pp_z[idx - 1]
            sigma = max(0.15, 0.20 + 0.03 * abs(gx - gy))
            w.writerow(
                [
                    f"L{idx:05d}",
                    ell,
                    f"{gx:.9f}",
                    f"{gy:.9f}",
                    f"{gx:.9f}",
                    f"{gy:.9f}",
                    f"{sigma:.9f}",
                    f"{mv_map[ell][1]:.12e}",
                    f"{pp_map[ell][1]:.12e}",
                ]
            )
    return len(common)


def parse_args() -> argparse.Namespace:
    mv_default, pp_default = default_nlkk_paths()
    p = argparse.ArgumentParser(description="Import DS-006 datasets from local downloads/extracted files.")
    p.add_argument("--rotmod-dir", default=str(DEFAULT_ROTMOD_DIR), help="Rotmod_LTG folder path.")
    p.add_argument("--mv-nlkk", default=str(mv_default), help="MV nlkk.dat path.")
    p.add_argument("--pp-nlkk", default=str(pp_default), help="PP nlkk.dat path.")
    p.add_argument("--rotation-out", default=str(DEFAULT_ROT_OUT), help="Output rotation CSV path.")
    p.add_argument("--lensing-out", default=str(DEFAULT_LENS_OUT), help="Output lensing CSV path.")
    p.add_argument("--ell-min", type=int, default=2, help="Minimum ell for lensing proxy.")
    p.add_argument("--ell-max", type=int, default=2048, help="Maximum ell for lensing proxy.")
    p.add_argument("--stride", type=int, default=8, help="Sample every N ell values.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    rotmod_dir = Path(args.rotmod_dir)
    mv_nlkk = Path(args.mv_nlkk)
    pp_nlkk = Path(args.pp_nlkk)
    rotation_out = Path(args.rotation_out)
    lensing_out = Path(args.lensing_out)

    if not rotmod_dir.exists():
        raise FileNotFoundError(f"Rotmod directory not found: {rotmod_dir}")
    if not mv_nlkk.exists():
        raise FileNotFoundError(f"MV nlkk not found: {mv_nlkk}")
    if not pp_nlkk.exists():
        raise FileNotFoundError(f"PP nlkk not found: {pp_nlkk}")

    rot_rows: list[RotRow] = []
    for path in sorted(rotmod_dir.glob("*_rotmod.dat")):
        rot_rows.extend(parse_rotmod_file(path))
    if len(rot_rows) < 20:
        raise RuntimeError(f"Too few parsed rotation rows: {len(rot_rows)}")
    write_rotation_csv(rot_rows, rotation_out)

    mv_map = read_nlkk(mv_nlkk)
    pp_map = read_nlkk(pp_nlkk)
    lens_count = write_lensing_proxy_csv(
        mv_map=mv_map,
        pp_map=pp_map,
        out_path=lensing_out,
        ell_min=args.ell_min,
        ell_max=args.ell_max,
        stride=max(1, args.stride),
    )
    if lens_count < 8:
        raise RuntimeError(f"Too few lensing rows written: {lens_count}")

    print(f"Rotation rows written: {len(rot_rows)} -> {rotation_out}")
    print(f"Lensing rows written: {lens_count} -> {lensing_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
