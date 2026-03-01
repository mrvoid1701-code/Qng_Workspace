#!/usr/bin/env python3
"""
Build DS-005 holdout rows for JUNO_1 / BEPICOLOMBO_1 / SOLAR_ORBITER_1
from JPL Horizons vector ephemerides.

Notes:
- Geometry fields are computed from Horizons vectors in Earth-centered frame.
- Inbound declination convention follows Anderson/Meessen-style table usage:
  delta_in is the negated median declination of inbound velocity samples.
- Residual anomaly columns are provisional placeholders (0 +/- 1 mm/s) until
  mission OD residual summaries are ingested.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import argparse
import csv
import math
import statistics


ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_holdout_from_horizons.csv"
TARGET_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
SOURCES_DIR = ROOT / "data" / "trajectory" / "sources" / "horizons"

MU_EARTH_KM3_S2 = 398600.4418


@dataclass(frozen=True)
class MissionCfg:
    pass_id: str
    mission_id: str
    command_id: str
    start_utc: str
    stop_utc: str
    event_date: str
    source_ref: str
    notes: str


MISSION_CFG = [
    MissionCfg(
        pass_id="JUNO_1",
        mission_id="Juno",
        command_id="-61",
        start_utc="2013-10-08 00:00",
        stop_utc="2013-10-11 00:00",
        event_date="2013-10-09",
        source_ref="Horizons_-61+JPL_OpenRepository_2014_45519",
        notes=(
            "Geometry from Horizons vectors; residual placeholder 0.0 +/- 1.0 mm/s. "
            "Juno reconstruction reports no anomalous velocity change near perigee."
        ),
    ),
    MissionCfg(
        pass_id="BEPICOLOMBO_1",
        mission_id="BepiColombo",
        command_id="-121",
        start_utc="2020-04-08 12:00",
        stop_utc="2020-04-11 12:00",
        event_date="2020-04-10",
        source_ref="Horizons_-121",
        notes=(
            "Geometry from Horizons vectors; residual placeholder 0.0 +/- 1.0 mm/s "
            "pending published OD flyby residual summary."
        ),
    ),
    MissionCfg(
        pass_id="SOLAR_ORBITER_1",
        mission_id="SolarOrbiter",
        command_id="-144",
        start_utc="2021-11-25 12:00",
        stop_utc="2021-11-28 12:00",
        event_date="2021-11-27",
        source_ref="Horizons_-144",
        notes=(
            "Geometry from Horizons vectors; residual placeholder 0.0 +/- 1.0 mm/s "
            "pending published OD flyby residual summary."
        ),
    ),
]


def horizons_url(params: dict[str, str]) -> str:
    return "https://ssd.jpl.nasa.gov/api/horizons.api?" + urlencode(params, safe="'@")


def fetch_text(params: dict[str, str]) -> str:
    with urlopen(horizons_url(params), timeout=180) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_vectors(text: str) -> list[tuple[float, str, float, float, float]]:
    rows: list[tuple[float, str, float, float, float]] = []
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if line == "$$SOE":
            in_block = True
            continue
        if line == "$$EOE":
            break
        if not in_block or not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8:
            continue
        try:
            jd = float(parts[0])
            cal = parts[1]
            x = float(parts[2])
            y = float(parts[3])
            z = float(parts[4])
            vx = float(parts[5])
            vy = float(parts[6])
            vz = float(parts[7])
        except ValueError:
            continue
        r = math.sqrt(x * x + y * y + z * z)
        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        dec_v = math.degrees(math.asin(max(-1.0, min(1.0, vz / max(v, 1e-12)))))
        rows.append((jd, cal, r, v, dec_v))
    return rows


def fmt(x: float, digits: int = 6) -> str:
    return f"{x:.{digits}f}"


def build_row(cfg: MissionCfg) -> dict[str, str]:
    summary_params = {
        "format": "text",
        "COMMAND": f"'{cfg.command_id}'",
    }
    vectors_params = {
        "format": "text",
        "COMMAND": f"'{cfg.command_id}'",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "500@399",
        "START_TIME": f"'{cfg.start_utc}'",
        "STOP_TIME": f"'{cfg.stop_utc}'",
        "STEP_SIZE": "'2m'",
        "VEC_TABLE": "2",
        "OUT_UNITS": "KM-S",
        "CSV_FORMAT": "YES",
        "REF_SYSTEM": "ICRF",
        "REF_PLANE": "FRAME",
    }

    summary_txt = fetch_text(summary_params)
    vectors_txt = fetch_text(vectors_params)

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    (SOURCES_DIR / f"{cfg.pass_id.lower()}_summary.txt").write_text(summary_txt, encoding="utf-8")
    (SOURCES_DIR / f"{cfg.pass_id.lower()}_vectors.txt").write_text(vectors_txt, encoding="utf-8")

    rows = parse_vectors(vectors_txt)
    if not rows:
        raise RuntimeError(f"No vector rows parsed for {cfg.pass_id}.")

    perigee = min(rows, key=lambda r: r[2])
    n = len(rows)
    k = max(1, int(0.10 * n))
    dec_in_vel = statistics.median([r[4] for r in rows[:k]])
    dec_out_vel = statistics.median([r[4] for r in rows[-k:]])

    # Convention match with Anderson/Meessen table style.
    delta_in_deg = -dec_in_vel
    delta_out_deg = dec_out_vel

    r_perigee_km = perigee[2]
    v_perigee_km_s = perigee[3]
    v_inf_km_s = math.sqrt(max(v_perigee_km_s * v_perigee_km_s - 2.0 * MU_EARTH_KM3_S2 / r_perigee_km, 0.0))

    return {
        "pass_id": cfg.pass_id,
        "mission_id": cfg.mission_id,
        "event_date": cfg.event_date,
        "r_perigee_km": fmt(r_perigee_km, 3),
        "v_inf_km_s": fmt(v_inf_km_s, 3),
        "delta_in_deg": fmt(delta_in_deg, 3),
        "delta_out_deg": fmt(delta_out_deg, 3),
        "delta_v_obs_mm_s": fmt(0.0, 2),
        "delta_v_sigma_mm_s": fmt(1.0, 2),
        "thermal_corr_mm_s": fmt(0.0, 1),
        "srp_corr_mm_s": fmt(0.0, 1),
        "maneuver_corr_mm_s": fmt(0.0, 1),
        "drag_corr_mm_s": fmt(0.0, 1),
        "trajectory_class": "flyby",
        "source_ref": cfg.source_ref,
        "notes": cfg.notes,
    }


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def merge_into_target(target_path: Path, new_rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    existing: list[dict[str, str]] = []
    if target_path.exists():
        with target_path.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                existing.append({k: row.get(k, "") for k in fieldnames})

    replace_ids = {row["pass_id"] for row in new_rows}
    kept = [row for row in existing if row.get("pass_id") not in replace_ids]
    merged = kept + new_rows
    write_rows(target_path, fieldnames, merged)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build DS-005 holdout rows from JPL Horizons.")
    p.add_argument("--apply", action="store_true", help="Also merge rows into data/trajectory/flyby_ds005_real.csv")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    fieldnames = [
        "pass_id",
        "mission_id",
        "event_date",
        "r_perigee_km",
        "v_inf_km_s",
        "delta_in_deg",
        "delta_out_deg",
        "delta_v_obs_mm_s",
        "delta_v_sigma_mm_s",
        "thermal_corr_mm_s",
        "srp_corr_mm_s",
        "maneuver_corr_mm_s",
        "drag_corr_mm_s",
        "trajectory_class",
        "source_ref",
        "notes",
    ]

    rows = [build_row(cfg) for cfg in MISSION_CFG]
    write_rows(OUT_CSV, fieldnames, rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")

    if args.apply:
        merge_into_target(TARGET_CSV, rows, fieldnames)
        print(f"Merged rows into {TARGET_CSV}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

