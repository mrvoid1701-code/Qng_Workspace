#!/usr/bin/env python3
"""
Real flyby trajectory diagnostics for QNG trajectory claims.

Targets:
- QNG-T-028
- QNG-T-041

Uses published Earth-flyby residual summaries (DS-005 real CSV), explicit
non-gravitational correction columns, and reviewer-style controls/robustness.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import json
import math
import random
import statistics
import time

import run_qng_t_028_trajectory as legacy


ROOT = Path(__file__).resolve().parent.parent
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"
DEFAULT_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
DEFAULT_PIONEER_CSV = ROOT / "data" / "trajectory" / "pioneer_ds005_anchor.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-028"

MU_EARTH = 3.986004418e14
MU_SUN = 1.32712440018e20
AU_M = 1.495978707e11


@dataclass
class Obs:
    pass_id: str
    mission_id: str
    x: float
    y: float
    sigma: float
    base_x: float
    scale: float
    is_control: bool
    is_symmetric: bool
    delta_in_deg: float
    delta_out_deg: float
    delta_cos: float
    data_domain: str


@dataclass
class Fit:
    tau: float
    chi2_b: float
    chi2_m: float
    dchi2: float
    aic_b: float
    aic_m: float
    daic: float
    bic_b: float
    bic_m: float
    dbic: float
    directionality: float
    n: int


def read_manifest(dataset_id: str) -> dict | None:
    if not DATASET_MANIFEST_JSON.exists():
        return None
    try:
        rows = json.loads(DATASET_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("dataset_id") == dataset_id:
            return row
    return None


def parse_real_csv(path: Path) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {
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
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        for row in reader:
            try:
                row["r_perigee_km"] = float(str(row["r_perigee_km"]).replace(",", ""))
                row["v_inf_km_s"] = float(str(row["v_inf_km_s"]).replace(",", ""))
                row["delta_in_deg"] = float(str(row["delta_in_deg"]).replace(",", ""))
                row["delta_out_deg"] = float(str(row["delta_out_deg"]).replace(",", ""))
                row["delta_v_obs_mm_s"] = float(str(row["delta_v_obs_mm_s"]).replace(",", ""))
                row["delta_v_sigma_mm_s"] = max(1e-6, float(str(row["delta_v_sigma_mm_s"]).replace(",", "")))
                row["thermal_corr_mm_s"] = float(str(row["thermal_corr_mm_s"]).replace(",", ""))
                row["srp_corr_mm_s"] = float(str(row["srp_corr_mm_s"]).replace(",", ""))
                row["maneuver_corr_mm_s"] = float(str(row["maneuver_corr_mm_s"]).replace(",", ""))
                row["drag_corr_mm_s"] = float(str(row["drag_corr_mm_s"]).replace(",", ""))
            except Exception:
                warnings.append(f"Skipping malformed row: {row.get('pass_id', 'unknown')}")
                continue
            rows.append(row)
    if not rows:
        raise ValueError("No usable rows in real flyby CSV.")
    return rows, warnings


def parse_pioneer_csv(path: Path) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "record_id",
            "mission_id",
            "interval_start",
            "interval_end",
            "r_au_mean",
            "v_km_s",
            "a_obs_m_s2",
            "a_sigma_m_s2",
            "bias_corr_m_s2",
            "source_ref",
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing pioneer columns: {', '.join(missing)}")
        for row in reader:
            try:
                row["r_au_mean"] = float(str(row["r_au_mean"]).replace(",", ""))
                row["v_km_s"] = float(str(row["v_km_s"]).replace(",", ""))
                row["a_obs_m_s2"] = float(str(row["a_obs_m_s2"]).replace(",", ""))
                row["a_sigma_m_s2"] = max(1e-14, float(str(row["a_sigma_m_s2"]).replace(",", "")))
                row["bias_corr_m_s2"] = float(str(row["bias_corr_m_s2"]).replace(",", ""))
            except Exception:
                warnings.append(f"Skipping malformed pioneer row: {row.get('record_id', 'unknown')}")
                continue
            rows.append(row)
    if not rows:
        raise ValueError("No usable rows in pioneer anchor CSV.")
    return rows, warnings


def build_observations(rows: list[dict]) -> tuple[list[Obs], list[Obs], list[Obs], list[dict]]:
    perigee: list[Obs] = []
    whole: list[Obs] = []
    mixed: list[Obs] = []
    derived: list[dict] = []

    for row in rows:
        rp = row["r_perigee_km"] * 1000.0
        v_inf = row["v_inf_km_s"] * 1000.0
        v_p = math.sqrt(v_inf * v_inf + 2.0 * MU_EARTH / rp)
        delta_cos = math.cos(math.radians(row["delta_in_deg"])) - math.cos(math.radians(row["delta_out_deg"]))
        base_x = (MU_EARTH / (rp ** 3)) * v_p * delta_cos

        corr = row["thermal_corr_mm_s"] + row["srp_corr_mm_s"] + row["maneuver_corr_mm_s"] + row["drag_corr_mm_s"]
        dv_corr_mm_s = row["delta_v_obs_mm_s"] - corr
        t_peri = rp / max(v_p, 1e-12)
        t_whole = 2.0 * t_peri
        y_peri = (dv_corr_mm_s * 1e-3) / t_peri
        y_whole = (dv_corr_mm_s * 1e-3) / t_whole
        s_peri = max((row["delta_v_sigma_mm_s"] * 1e-3) / t_peri, 1e-14)
        s_whole = max((row["delta_v_sigma_mm_s"] * 1e-3) / t_whole, 1e-14)
        is_control = "control" in str(row["trajectory_class"]).lower()
        is_symmetric = abs(delta_cos) <= 0.08

        a = Obs(
            row["pass_id"],
            row["mission_id"],
            base_x,
            y_peri,
            s_peri,
            base_x,
            1.0,
            is_control,
            is_symmetric,
            row["delta_in_deg"],
            row["delta_out_deg"],
            delta_cos,
            "flyby_real",
        )
        b = Obs(
            row["pass_id"],
            row["mission_id"],
            base_x * 0.5,
            y_whole,
            s_whole,
            base_x,
            0.5,
            is_control,
            is_symmetric,
            row["delta_in_deg"],
            row["delta_out_deg"],
            delta_cos,
            "flyby_real",
        )
        perigee.append(a)
        whole.append(b)
        mixed.extend([a, b])

        y_day = (dv_corr_mm_s * 1e-3) / 86400.0

        derived.append(
            {
                "pass_id": row["pass_id"],
                "mission_id": row["mission_id"],
                "event_date": row["event_date"],
                "r_perigee_km": legacy.fmt(row["r_perigee_km"]),
                "v_inf_km_s": legacy.fmt(row["v_inf_km_s"]),
                "delta_in_deg": legacy.fmt(row["delta_in_deg"]),
                "delta_out_deg": legacy.fmt(row["delta_out_deg"]),
                "delta_cos": legacy.fmt(delta_cos),
                "delta_v_obs_mm_s": legacy.fmt(row["delta_v_obs_mm_s"]),
                "corrections_total_mm_s": legacy.fmt(corr),
                "delta_v_corrected_mm_s": legacy.fmt(dv_corr_mm_s),
                "a_obs_perigee_m_s2": legacy.fmt(y_peri),
                "a_obs_whole_m_s2": legacy.fmt(y_whole),
                "a_obs_day_equiv_m_s2": legacy.fmt(y_day),
                "sigma_perigee_m_s2": legacy.fmt(s_peri),
                "sigma_whole_m_s2": legacy.fmt(s_whole),
                "feature_base_m_s3": legacy.fmt(base_x),
                "is_control": str(is_control),
                "is_symmetric": str(is_symmetric),
                "data_domain": "flyby_real",
                "record_id": row["pass_id"],
                "a_obs_raw_m_s2": legacy.fmt(y_peri),
                "correction_applied_m_s2": legacy.fmt(0.0),
                "trajectory_class": row["trajectory_class"],
                "source_ref": row["source_ref"],
            }
        )

    return perigee, whole, mixed, derived


def build_pioneer_observations(rows: list[dict]) -> tuple[list[Obs], list[Obs], list[Obs], list[Obs], list[dict]]:
    perigee: list[Obs] = []
    whole: list[Obs] = []
    mixed: list[Obs] = []
    raw_only: list[Obs] = []
    derived: list[dict] = []

    for row in rows:
        r_m = row["r_au_mean"] * AU_M
        v_m_s = row["v_km_s"] * 1000.0
        base_x = MU_SUN / max(r_m * r_m, 1e-30)
        y_raw = row["a_obs_m_s2"]
        corr = row["bias_corr_m_s2"]
        y_corr = y_raw - corr
        sigma = row["a_sigma_m_s2"]

        obs_corr = Obs(
            row["record_id"],
            row["mission_id"],
            base_x,
            y_corr,
            sigma,
            base_x,
            1.0,
            False,
            False,
            0.0,
            0.0,
            1.0,
            "pioneer_anchor",
        )
        obs_raw = Obs(
            row["record_id"],
            row["mission_id"],
            base_x,
            y_raw,
            sigma,
            base_x,
            1.0,
            False,
            False,
            0.0,
            0.0,
            1.0,
            "pioneer_anchor_raw",
        )
        # Deep-space anchors are acceleration summaries, so whole/perigee are identical.
        perigee.append(obs_corr)
        whole.append(obs_corr)
        mixed.extend([obs_corr, obs_corr])
        raw_only.append(obs_raw)

        derived.append(
            {
                "pass_id": row["record_id"],
                "mission_id": row["mission_id"],
                "event_date": row["interval_end"],
                "r_perigee_km": legacy.fmt(r_m / 1000.0),
                "v_inf_km_s": legacy.fmt(row["v_km_s"]),
                "delta_in_deg": legacy.fmt(0.0),
                "delta_out_deg": legacy.fmt(0.0),
                "delta_cos": legacy.fmt(1.0),
                "delta_v_obs_mm_s": legacy.fmt(y_raw * 1e3),
                "corrections_total_mm_s": legacy.fmt(corr * 1e3),
                "delta_v_corrected_mm_s": legacy.fmt(y_corr * 1e3),
                "a_obs_perigee_m_s2": legacy.fmt(y_corr),
                "a_obs_whole_m_s2": legacy.fmt(y_corr),
                "a_obs_day_equiv_m_s2": legacy.fmt(y_corr),
                "sigma_perigee_m_s2": legacy.fmt(sigma),
                "sigma_whole_m_s2": legacy.fmt(sigma),
                "feature_base_m_s3": legacy.fmt(base_x),
                "is_control": str(False),
                "is_symmetric": str(False),
                "data_domain": "pioneer_anchor",
                "record_id": row["record_id"],
                "a_obs_raw_m_s2": legacy.fmt(y_raw),
                "correction_applied_m_s2": legacy.fmt(corr),
                "trajectory_class": "deep_space_anchor",
                "source_ref": row["source_ref"],
            }
        )
    return perigee, whole, mixed, raw_only, derived


def fit(obs: list[Obs], x_override: list[float] | None = None) -> Fit:
    if not obs:
        return Fit(0.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, 0)
    xs = x_override if x_override is not None else [o.x for o in obs]
    ys = [o.y for o in obs]
    sig = [o.sigma for o in obs]
    n = len(obs)

    num = 0.0
    den = 0.0
    chi2_b = 0.0
    for x, y, s in zip(xs, ys, sig):
        w = 1.0 / max(s * s, 1e-30)
        num += w * x * y
        den += w * x * x
        chi2_b += w * y * y
    tau = num / den if den > 1e-30 else 0.0
    chi2_m = sum((1.0 / max(s * s, 1e-30)) * (y - tau * x) ** 2 for x, y, s in zip(xs, ys, sig))
    agree = [1.0 if (x * y) >= 0 else 0.0 for x, y in zip(xs, ys) if abs(x) > 1e-18 and abs(y) > 1e-18]
    directionality = statistics.fmean(agree) if agree else 0.0
    aic_b = chi2_b
    aic_m = chi2_m + 2.0
    bic_b = chi2_b
    bic_m = chi2_m + math.log(max(1, n))
    return Fit(tau, chi2_b, chi2_m, chi2_m - chi2_b, aic_b, aic_m, aic_m - aic_b, bic_b, bic_m, bic_m - bic_b, directionality, n)


def fit_by_mission(obs: list[Obs], tau_global: float) -> tuple[list[dict], float, float]:
    groups: dict[str, list[Obs]] = {}
    for o in obs:
        groups.setdefault(o.mission_id, []).append(o)
    rows: list[dict] = []
    tau_vals: list[float] = []
    sign_ok: list[float] = []
    for mission_id, items in sorted(groups.items()):
        fr = fit(items)
        if len(items) >= 2:
            tau_vals.append(fr.tau)
        if abs(fr.tau) > 1e-30 and abs(tau_global) > 1e-30:
            sign_ok.append(1.0 if fr.tau * tau_global >= 0 else 0.0)
        rows.append(
            {
                "mission_id": mission_id,
                "n_points": str(len(items)),
                "tau_hat": legacy.fmt(fr.tau),
                "directionality": legacy.fmt(fr.directionality),
                "amp_median": legacy.fmt(statistics.median([abs(tau_global * o.x) for o in items])),
            }
        )
    tau_cv = (
        statistics.pstdev(tau_vals) / abs(statistics.fmean(tau_vals))
        if len(tau_vals) >= 2 and abs(statistics.fmean(tau_vals)) > 1e-30
        else 0.0
    )
    sign_consistency = statistics.fmean(sign_ok) if sign_ok else 0.0
    return rows, tau_cv, sign_consistency


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_id_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG trajectory REAL diagnostics.")
    p.add_argument("--test-id", default="QNG-T-028")
    p.add_argument("--dataset-id", default="DS-005")
    p.add_argument("--flyby-csv", default=str(DEFAULT_CSV))
    p.add_argument("--use-pioneer-anchor", action="store_true")
    p.add_argument("--pioneer-csv", default=str(DEFAULT_PIONEER_CSV))
    p.add_argument("--flyby-pass-ids", default="", help="Optional comma-separated flyby pass_id filter.")
    p.add_argument("--pioneer-record-ids", default="", help="Optional comma-separated pioneer record_id filter.")
    p.add_argument(
        "--amp-gate-mode",
        choices=["report-only", "strict"],
        default="report-only",
        help="Amplitude-band handling for QNG-T-041 (report-only or strict).",
    )
    p.add_argument("--amp-band-min", type=float, default=1e-10, help="Lower amplitude bound for strict amp gate.")
    p.add_argument("--amp-band-max", type=float, default=1e-8, help="Upper amplitude bound for strict amp gate.")
    p.add_argument("--n-control-runs", type=int, default=400)
    p.add_argument("--leave-out-runs", type=int, default=96)
    p.add_argument("--seed", type=int, default=20260217)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    warnings: list[str] = []
    manifest_row = read_manifest(args.dataset_id)
    if manifest_row is None:
        warnings.append(f"Dataset id '{args.dataset_id}' not found in dataset-manifest.json")

    flyby_csv = Path(args.flyby_csv)
    if not flyby_csv.is_absolute():
        flyby_csv = (ROOT / flyby_csv).resolve()
    rows, csv_warnings = parse_real_csv(flyby_csv)
    warnings.extend(csv_warnings)
    flyby_filter_ids = set(parse_id_list(args.flyby_pass_ids))
    if flyby_filter_ids:
        before = len(rows)
        rows = [r for r in rows if str(r.get("pass_id", "")) in flyby_filter_ids]
        missing_ids = sorted(flyby_filter_ids - {str(r.get("pass_id", "")) for r in rows})
        if missing_ids:
            warnings.append(f"Flyby pass_id filter missing rows: {', '.join(missing_ids)}")
        warnings.append(f"Flyby filter active: kept {len(rows)} of {before} rows.")

    perigee, whole, mixed, derived = build_observations(rows)
    pioneer_rows: list[dict] = []
    pioneer_raw_obs: list[Obs] = []
    if args.use_pioneer_anchor:
        pioneer_csv = Path(args.pioneer_csv)
        if not pioneer_csv.is_absolute():
            pioneer_csv = (ROOT / pioneer_csv).resolve()
        p_rows, p_warnings = parse_pioneer_csv(pioneer_csv)
        warnings.extend(p_warnings)

        pioneer_filter_ids = set(parse_id_list(args.pioneer_record_ids))
        if pioneer_filter_ids:
            before = len(p_rows)
            p_rows = [r for r in p_rows if str(r.get("record_id", "")) in pioneer_filter_ids]
            missing_ids = sorted(pioneer_filter_ids - {str(r.get("record_id", "")) for r in p_rows})
            if missing_ids:
                warnings.append(f"Pioneer record_id filter missing rows: {', '.join(missing_ids)}")
            warnings.append(f"Pioneer filter active: kept {len(p_rows)} of {before} rows.")

        pioneer_rows = p_rows
        p_perigee, p_whole, p_mixed, p_raw, p_derived = build_pioneer_observations(p_rows)
        perigee.extend(p_perigee)
        whole.extend(p_whole)
        mixed.extend(p_mixed)
        pioneer_raw_obs.extend(p_raw)
        derived.extend(p_derived)

    science_perigee = [o for o in perigee if not (o.is_control or o.is_symmetric)]
    science_whole = [o for o in whole if not (o.is_control or o.is_symmetric)]
    science_mixed = [o for o in mixed if not (o.is_control or o.is_symmetric)]
    control_obs = [o for o in perigee if (o.is_control or o.is_symmetric)]

    if len(science_perigee) < 3:
        warnings.append("Science subset has fewer than 3 rows; fallback to non-control rows.")
        science_perigee = [o for o in perigee if not o.is_control]
        science_whole = [o for o in whole if not o.is_control]
        science_mixed = [o for o in mixed if not o.is_control]
        control_obs = [o for o in perigee if o.is_control]
    if len(science_perigee) < 3:
        warnings.append("Science subset still fewer than 3 rows; fallback to all rows.")
        science_perigee = list(perigee)
        science_whole = list(whole)
        science_mixed = list(mixed)
        control_obs = []

    fit_p = fit(science_perigee)
    fit_w = fit(science_whole)
    fit_mixed = fit(science_mixed)
    mission_rows, tau_cv_mission, sign_consistency = fit_by_mission(science_perigee, fit_p.tau)
    science_flyby = [o for o in science_perigee if o.data_domain == "flyby_real"]
    science_pioneer = [o for o in science_perigee if o.data_domain == "pioneer_anchor"]
    science_flyby_mixed = [o for o in science_mixed if o.data_domain == "flyby_real"]
    fit_flyby = fit(science_flyby) if science_flyby else Fit(0.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, 0.0, 0)
    fit_pioneer = fit(science_pioneer) if science_pioneer else Fit(0.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, 0.0, 0)
    fit_pioneer_raw = fit(pioneer_raw_obs) if pioneer_raw_obs else Fit(0.0, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, 0.0, 0)
    shuffle_perigee = science_flyby if (args.use_pioneer_anchor and len(science_flyby) >= 3) else science_perigee
    shuffle_mixed = science_flyby_mixed if (args.use_pioneer_anchor and len(science_flyby_mixed) >= 6) else science_mixed

    rng = random.Random(args.seed)
    shuf_dchi2 = []
    base_x = [o.x for o in shuffle_perigee]
    for _ in range(max(32, args.n_control_runs)):
        perm = base_x[:]
        rng.shuffle(perm)
        shuf_dchi2.append(fit(shuffle_perigee, perm).dchi2)
    orient_med = statistics.median(shuf_dchi2)
    orient_target = fit(shuffle_perigee).dchi2
    orient_p = sum(1 for v in shuf_dchi2 if v <= orient_target) / max(1, len(shuf_dchi2))
    orient_ratio = abs(orient_med / orient_target) if abs(orient_target) > 1e-30 else float("inf")

    scale_list = [o.scale for o in shuffle_mixed]
    seg_dchi2 = []
    for _ in range(max(32, args.n_control_runs)):
        perm_scale = scale_list[:]
        rng.shuffle(perm_scale)
        x_perm = [o.base_x * s for o, s in zip(shuffle_mixed, perm_scale)]
        seg_dchi2.append(fit(shuffle_mixed, x_perm).dchi2)
    seg_target = fit(shuffle_mixed).dchi2
    seg_med = statistics.median(seg_dchi2)
    seg_p = sum(1 for v in seg_dchi2 if v <= seg_target) / max(1, len(seg_dchi2))
    seg_ratio = abs(seg_med / seg_target) if abs(seg_target) > 1e-30 else float("inf")

    control_abs_mean = statistics.fmean([abs(o.y) for o in control_obs]) if control_obs else 0.0
    control_sigma_mean = statistics.fmean([o.sigma for o in control_obs]) if control_obs else 1.0
    control_z_mean = statistics.fmean([abs(o.y) / max(o.sigma, 1e-30) for o in control_obs]) if control_obs else 0.0

    stability_obs = science_flyby if (args.use_pioneer_anchor and len(science_flyby) >= 3) else science_perigee
    leave_dchi2: list[float] = []
    leave_daic: list[float] = []
    leave_dbic: list[float] = []
    leave_tau: list[float] = []
    leave_pass = 0
    n = len(stability_obs)
    keep_n = max(1, n - max(1, int(math.ceil(0.10 * n))))
    idx = list(range(n))
    for _ in range(max(24, args.leave_out_runs)):
        keep = set(rng.sample(idx, keep_n))
        sub = [o for i, o in enumerate(stability_obs) if i in keep]
        fr = fit(sub)
        leave_dchi2.append(fr.dchi2)
        leave_daic.append(fr.daic)
        leave_dbic.append(fr.dbic)
        leave_tau.append(fr.tau)
        if (fr.dchi2 < 0.0) and (fr.daic <= -2.0) and (fr.dbic <= -2.0):
            leave_pass += 1
    leave_pass_fraction = leave_pass / max(1, len(leave_dchi2))
    tau_cv_leave = (
        statistics.pstdev(leave_tau) / abs(statistics.fmean(leave_tau))
        if len(leave_tau) >= 2 and abs(statistics.fmean(leave_tau)) > 1e-30
        else 0.0
    )

    z_sorted = sorted(((abs(o.y - fit_p.tau * o.x) / max(o.sigma, 1e-30), o) for o in science_perigee), key=lambda t: t[0])
    trim_n = max(1, int(math.ceil(0.10 * len(science_perigee))))
    kept = [o for _, o in z_sorted[: max(1, len(science_perigee) - trim_n)]]
    fit_trim = fit(kept)
    trim_pass = (fit_trim.dchi2 < 0.0) and (fit_trim.daic <= -2.0) and (fit_trim.dbic <= -2.0)

    in_rows: list[Obs] = []
    out_rows: list[Obs] = []
    for o in science_perigee:
        grad = abs(o.base_x) / max(abs(o.delta_cos), 1e-30) if abs(o.delta_cos) > 1e-30 else 0.0
        c_in = math.cos(math.radians(o.delta_in_deg))
        c_out = math.cos(math.radians(o.delta_out_deg))
        y_half = 0.5 * o.y
        s_half = max(o.sigma / math.sqrt(2.0), 1e-14)
        in_rows.append(
            Obs(
                o.pass_id,
                o.mission_id,
                grad * c_in,
                y_half,
                s_half,
                grad * c_in,
                1.0,
                False,
                False,
                o.delta_in_deg,
                o.delta_out_deg,
                o.delta_cos,
                "derived_io",
            )
        )
        out_rows.append(
            Obs(
                o.pass_id,
                o.mission_id,
                -grad * c_out,
                y_half,
                s_half,
                -grad * c_out,
                1.0,
                False,
                False,
                o.delta_in_deg,
                o.delta_out_deg,
                o.delta_cos,
                "derived_io",
            )
        )
    fit_in = fit(in_rows)
    fit_out = fit(out_rows)

    amp_vals = [abs(o.y) for o in science_perigee]
    amp_median = statistics.median(amp_vals) if amp_vals else 0.0
    science_pass_ids = {o.pass_id for o in science_perigee}
    day_vals = [
        abs(float(d["a_obs_day_equiv_m_s2"]))
        for d in derived
        if d["pass_id"] in science_pass_ids and d["a_obs_day_equiv_m_s2"] not in {"nan", "inf"}
    ]
    amp_median_day = statistics.median(day_vals) if day_vals else 0.0
    amp_band_min = min(args.amp_band_min, args.amp_band_max)
    amp_band_max = max(args.amp_band_min, args.amp_band_max)
    amp_band_ok_strict = amp_band_min <= amp_median <= amp_band_max
    amp_band_ok_day = amp_band_min <= amp_median_day <= amp_band_max

    tau_ratio_pw = abs(fit_w.tau / fit_p.tau) if abs(fit_p.tau) > 1e-30 else float("inf")
    tau_ratio_io = max(abs(fit_in.tau), abs(fit_out.tau)) / max(min(abs(fit_in.tau), abs(fit_out.tau)), 1e-30)
    tau_ratio_cross_domain = (
        max(abs(fit_flyby.tau), abs(fit_pioneer.tau)) / max(min(abs(fit_flyby.tau), abs(fit_pioneer.tau)), 1e-30)
        if (science_flyby and science_pioneer)
        else float("inf")
    )
    pioneer_corr_present = any(abs(r.get("bias_corr_m_s2", 0.0)) > 0.0 for r in pioneer_rows)
    pioneer_postcorr_ok = (fit_pioneer.dchi2 < 0.0) and (fit_pioneer.daic <= -2.0) and (fit_pioneer.dbic <= -2.0)
    pioneer_domain_ok = (
        (len(science_pioneer) >= 2)
        and pioneer_postcorr_ok
        and (fit_pioneer.tau * fit_flyby.tau >= 0.0 if science_flyby else True)
        and (tau_ratio_cross_domain <= 25.0)
    )

    amp_gate_strict = (args.test_id.upper() == "QNG-T-041") and (args.amp_gate_mode == "strict")

    rules = {
        "rule_pass_delta_chi2": fit_p.dchi2 < 0.0,
        "rule_pass_delta_aic": fit_p.daic <= -10.0,
        "rule_pass_delta_bic": fit_p.dbic <= -10.0,
        "rule_pass_directionality": fit_p.directionality >= 0.70,
        "rule_pass_sign_consistency": sign_consistency >= (2.0 / 3.0),
        "rule_pass_stability": (not math.isinf(tau_cv_leave)) and (tau_cv_leave <= 0.50),
        "rule_pass_control_zero": (not control_obs) or (control_z_mean <= 1.50),
        "rule_pass_orientation_shuffle": (orient_p <= 0.10) and (orient_ratio <= 0.35),
        "rule_pass_segment_shuffle": (seg_p <= 0.10) and (seg_ratio <= 0.95),
        "rule_pass_perigee_whole": (fit_p.tau * fit_w.tau >= 0.0) and (0.85 <= tau_ratio_pw <= 1.20),
        "rule_pass_inbound_outbound": (fit_in.tau * fit_out.tau <= 0.0) and (tau_ratio_io <= 3.0),
        "rule_pass_leave_out": leave_pass_fraction >= 0.90,
        "rule_pass_outlier_trim": trim_pass,
        "rule_pass_amp_band": amp_band_ok_strict if amp_gate_strict else True,
        "rule_pass_pioneer_domain": pioneer_domain_ok if args.use_pioneer_anchor else True,
        "rule_pass_pioneer_postcorr": pioneer_postcorr_ok if args.use_pioneer_anchor else True,
    }
    required_rules = [
        "rule_pass_delta_chi2",
        "rule_pass_delta_aic",
        "rule_pass_delta_bic",
        "rule_pass_directionality",
        "rule_pass_sign_consistency",
        "rule_pass_stability",
        "rule_pass_control_zero",
        "rule_pass_orientation_shuffle",
        "rule_pass_segment_shuffle",
        "rule_pass_perigee_whole",
        "rule_pass_inbound_outbound",
        "rule_pass_leave_out",
        "rule_pass_outlier_trim",
    ]
    if amp_gate_strict:
        required_rules.append("rule_pass_amp_band")
    if args.use_pioneer_anchor and args.test_id.upper() in {"QNG-T-028", "QNG-T-011", "QNG-T-041"}:
        required_rules.append("rule_pass_pioneer_domain")
        required_rules.append("rule_pass_pioneer_postcorr")
    recommendation = "pass" if all(rules.get(k, False) for k in required_rules) else "fail"

    write_csv_rows(out_dir / "flyby-derived.csv", fieldnames=list(derived[0].keys()), rows=derived)
    write_csv_rows(
        out_dir / "mission-fits.csv",
        fieldnames=["mission_id", "n_points", "tau_hat", "directionality", "amp_median"],
        rows=mission_rows,
    )

    neg_summary = {
        "n_orientation_runs": str(len(shuf_dchi2)),
        "orientation_median_delta_chi2": legacy.fmt(orient_med),
        "orientation_ratio_vs_real": legacy.fmt(orient_ratio),
        "orientation_p_value": legacy.fmt(orient_p),
        "n_segment_runs": str(len(seg_dchi2)),
        "segment_median_delta_chi2": legacy.fmt(seg_med),
        "segment_ratio_vs_real": legacy.fmt(seg_ratio),
        "segment_p_value": legacy.fmt(seg_p),
        "control_mean_abs_accel": legacy.fmt(control_abs_mean),
        "control_mean_sigma": legacy.fmt(control_sigma_mean),
        "control_mean_abs_over_sigma": legacy.fmt(control_z_mean),
        "n_controls": str(len(control_obs)),
        "rule_pass_orientation_shuffle": str(rules["rule_pass_orientation_shuffle"]),
        "rule_pass_segment_shuffle": str(rules["rule_pass_segment_shuffle"]),
        "rule_pass_control_zero": str(rules["rule_pass_control_zero"]),
        "negative_control_pass": str(
            rules["rule_pass_orientation_shuffle"] and rules["rule_pass_segment_shuffle"] and rules["rule_pass_control_zero"]
        ),
    }
    legacy.write_csv_dict(out_dir / "negative-controls-summary.csv", neg_summary)

    robust_csv = {
        "tau_perigee": legacy.fmt(fit_p.tau),
        "tau_whole": legacy.fmt(fit_w.tau),
        "tau_inbound": legacy.fmt(fit_in.tau),
        "tau_outbound": legacy.fmt(fit_out.tau),
        "tau_flyby": legacy.fmt(fit_flyby.tau),
        "tau_pioneer": legacy.fmt(fit_pioneer.tau),
        "tau_pioneer_raw": legacy.fmt(fit_pioneer_raw.tau),
        "tau_ratio_whole_perigee": legacy.fmt(tau_ratio_pw),
        "tau_ratio_inbound_outbound": legacy.fmt(tau_ratio_io),
        "tau_ratio_cross_domain": legacy.fmt(tau_ratio_cross_domain),
        "tau_cv_mission": legacy.fmt(tau_cv_mission),
        "tau_cv_leave_out": legacy.fmt(tau_cv_leave),
        "leave_out_runs": str(len(leave_dchi2)),
        "leave_out_keep_n": str(keep_n),
        "leave_out_delta_chi2_median": legacy.fmt(statistics.median(leave_dchi2)),
        "leave_out_delta_aic_median": legacy.fmt(statistics.median(leave_daic)),
        "leave_out_delta_bic_median": legacy.fmt(statistics.median(leave_dbic)),
        "leave_out_pass_fraction": legacy.fmt(leave_pass_fraction),
        "outlier_trim_removed_n": str(trim_n),
        "outlier_trim_kept_n": str(len(kept)),
        "outlier_trim_delta_chi2": legacy.fmt(fit_trim.dchi2),
        "outlier_trim_delta_aic": legacy.fmt(fit_trim.daic),
        "outlier_trim_delta_bic": legacy.fmt(fit_trim.dbic),
        "rule_pass_perigee_whole": str(rules["rule_pass_perigee_whole"]),
        "rule_pass_inbound_outbound": str(rules["rule_pass_inbound_outbound"]),
        "rule_pass_pioneer_domain": str(rules["rule_pass_pioneer_domain"]),
        "rule_pass_pioneer_postcorr": str(rules["rule_pass_pioneer_postcorr"]),
        "rule_pass_leave_out": str(rules["rule_pass_leave_out"]),
        "rule_pass_outlier_trim": str(rules["rule_pass_outlier_trim"]),
    }
    legacy.write_csv_dict(out_dir / "robustness-checks.csv", robust_csv)

    summary = {
        "test_id": args.test_id,
        "dataset_id": args.dataset_id,
        "data_source_mode": "real_published_flyby",
        "n_points": str(fit_p.n),
        "n_points_total": str(len(perigee)),
        "n_controls": str(len(control_obs)),
        "n_science_flyby": str(len(science_flyby)),
        "n_science_pioneer": str(len(science_pioneer)),
        "n_missions": str(len(mission_rows)),
        "tau_fit": legacy.fmt(fit_p.tau),
        "tau_fit_flyby": legacy.fmt(fit_flyby.tau),
        "tau_fit_pioneer": legacy.fmt(fit_pioneer.tau),
        "tau_fit_pioneer_raw": legacy.fmt(fit_pioneer_raw.tau),
        "chi2_baseline": legacy.fmt(fit_p.chi2_b),
        "chi2_memory": legacy.fmt(fit_p.chi2_m),
        "delta_chi2": legacy.fmt(fit_p.dchi2),
        "delta_chi2_flyby": legacy.fmt(fit_flyby.dchi2),
        "delta_chi2_pioneer": legacy.fmt(fit_pioneer.dchi2),
        "delta_chi2_pioneer_raw": legacy.fmt(fit_pioneer_raw.dchi2),
        "delta_chi2_whole": legacy.fmt(fit_w.dchi2),
        "delta_chi2_per_point_total": legacy.fmt(fit_p.dchi2 / max(1, fit_p.n)),
        "aic_baseline": legacy.fmt(fit_p.aic_b),
        "aic_memory": legacy.fmt(fit_p.aic_m),
        "delta_aic": legacy.fmt(fit_p.daic),
        "delta_aic_whole": legacy.fmt(fit_w.daic),
        "bic_baseline": legacy.fmt(fit_p.bic_b),
        "bic_memory": legacy.fmt(fit_p.bic_m),
        "delta_bic": legacy.fmt(fit_p.dbic),
        "delta_bic_whole": legacy.fmt(fit_w.dbic),
        "directionality_score": legacy.fmt(fit_p.directionality),
        "sign_consistency": legacy.fmt(sign_consistency),
        "amp_median": legacy.fmt(amp_median),
        "amp_median_day_equiv": legacy.fmt(amp_median_day),
        "amp_band_min": legacy.fmt(amp_band_min),
        "amp_band_max": legacy.fmt(amp_band_max),
        "amp_in_claim_band": str(amp_band_ok_strict),
        "amp_in_claim_band_day_equiv": str(amp_band_ok_day),
        "amp_gate_mode": args.amp_gate_mode,
        "cv_tau": legacy.fmt(tau_cv_leave),
        "cv_tau_mission": legacy.fmt(tau_cv_mission),
        "tau_ratio_cross_domain": legacy.fmt(tau_ratio_cross_domain),
        "pioneer_correction_present": str(pioneer_corr_present),
        "leave_out_pass_fraction": legacy.fmt(leave_pass_fraction),
        "outlier_trim_delta_chi2": legacy.fmt(fit_trim.dchi2),
        "outlier_trim_delta_aic": legacy.fmt(fit_trim.daic),
        "outlier_trim_delta_bic": legacy.fmt(fit_trim.dbic),
        "required_rules": ",".join(required_rules),
        "pass_recommendation": recommendation,
    }
    for key, value in rules.items():
        summary[key] = str(value)
    legacy.write_csv_dict(out_dir / "fit-summary.csv", summary)

    x_idx = [float(i + 1) for i in range(len(science_perigee))]
    y_obs = [o.y for o in science_perigee]
    y_mem = [fit_p.tau * o.x for o in science_perigee]
    legacy.plot_series_png(
        out_dir / "trajectory-residuals.png",
        x_idx,
        [
            ("obs", y_obs, (35, 97, 185)),
            ("baseline", [0.0] * len(y_obs), (160, 165, 170)),
            ("memory", y_mem, (22, 148, 112)),
        ],
    )
    pairs = sorted([(o.x, o.y) for o in science_perigee], key=lambda t: t[0])
    legacy.plot_series_png(out_dir / "directionality.png", [p[0] for p in pairs], [("obs", [p[1] for p in pairs], (211, 112, 55)), ("fit", [fit_p.tau * p[0] for p in pairs], (31, 132, 96))])

    write_md(
        out_dir / "model-comparison.md",
        [
            "# Model Comparison",
            "",
            "| Check | Baseline | Memory | Status |",
            "| --- | --- | --- | --- |",
            f"| Sample rows | n={fit_p.n} | n={fit_p.n} | pass |",
            "| Sigma weights | published pass-level sigma | same sigma rows | pass |",
            "| Likelihood form | weighted chi-square | weighted chi-square | pass |",
            "| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |",
            f"| Perigee vs whole | dchi2={legacy.fmt(fit_p.dchi2)} | dchi2={legacy.fmt(fit_w.dchi2)} | {'pass' if rules['rule_pass_perigee_whole'] else 'fail'} |",
            f"| Flyby vs Pioneer domain | tau_flyby={legacy.fmt(fit_flyby.tau)} | tau_pioneer={legacy.fmt(fit_pioneer.tau)} | {'pass' if rules['rule_pass_pioneer_domain'] else 'fail'} |",
            f"| Pioneer correction stage | raw dchi2={legacy.fmt(fit_pioneer_raw.dchi2)} | corrected dchi2={legacy.fmt(fit_pioneer.dchi2)} | {'pass' if rules['rule_pass_pioneer_postcorr'] else 'fail'} |",
            "",
            "| Metric | Baseline | Memory | Delta |",
            "| --- | --- | --- | --- |",
            f"| chi2_total | {legacy.fmt(fit_p.chi2_b)} | {legacy.fmt(fit_p.chi2_m)} | {legacy.fmt(fit_p.dchi2)} |",
            f"| AIC_total | {legacy.fmt(fit_p.aic_b)} | {legacy.fmt(fit_p.aic_m)} | {legacy.fmt(fit_p.daic)} |",
            f"| BIC_total | {legacy.fmt(fit_p.bic_b)} | {legacy.fmt(fit_p.bic_m)} | {legacy.fmt(fit_p.dbic)} |",
        ],
    )
    write_md(
        out_dir / "negative-controls.md",
        [
            "# Negative Controls",
            "",
            "## Orientation shuffle",
            f"- runs: `{len(shuf_dchi2)}`",
            f"- median delta_chi2: `{legacy.fmt(orient_med)}`",
            f"- p-value: `{legacy.fmt(orient_p)}`",
            f"- ratio_vs_real: `{legacy.fmt(orient_ratio)}`",
            "",
            "## Segment shuffle",
            f"- runs: `{len(seg_dchi2)}`",
            f"- median delta_chi2: `{legacy.fmt(seg_med)}`",
            f"- p-value: `{legacy.fmt(seg_p)}`",
            f"- ratio_vs_real: `{legacy.fmt(seg_ratio)}`",
            "",
            "## Symmetric/control subset (C-067)",
            f"- control_n: `{len(control_obs)}`",
            f"- mean |a_obs|: `{legacy.fmt(control_abs_mean)}`",
            f"- mean sigma: `{legacy.fmt(control_sigma_mean)}`",
            f"- mean |a_obs|/sigma: `{legacy.fmt(control_z_mean)}`",
        ],
    )
    write_md(
        out_dir / "robustness-checks.md",
        [
            "# Robustness Checks",
            "",
            f"- tau_perigee: `{legacy.fmt(fit_p.tau)}`",
            f"- tau_whole: `{legacy.fmt(fit_w.tau)}`",
            f"- tau_inbound: `{legacy.fmt(fit_in.tau)}`",
            f"- tau_outbound: `{legacy.fmt(fit_out.tau)}`",
            f"- tau_flyby: `{legacy.fmt(fit_flyby.tau)}`",
            f"- tau_pioneer: `{legacy.fmt(fit_pioneer.tau)}`",
            f"- tau_pioneer_raw: `{legacy.fmt(fit_pioneer_raw.tau)}`",
            f"- tau_ratio_whole_perigee: `{legacy.fmt(tau_ratio_pw)}`",
            f"- tau_ratio_inbound_outbound: `{legacy.fmt(tau_ratio_io)}`",
            f"- tau_ratio_cross_domain: `{legacy.fmt(tau_ratio_cross_domain)}`",
            f"- tau_cv_leave_out: `{legacy.fmt(tau_cv_leave)}`",
            f"- leave_out_pass_fraction: `{legacy.fmt(leave_pass_fraction)}`",
            f"- outlier_trim_delta_chi2: `{legacy.fmt(fit_trim.dchi2)}`",
            f"- outlier_trim_delta_aic: `{legacy.fmt(fit_trim.daic)}`",
            f"- outlier_trim_delta_bic: `{legacy.fmt(fit_trim.dbic)}`",
        ],
    )
    write_md(
        out_dir / "parameter-stability.md",
        [
            "# Parameter Stability - QNG Trajectory REAL",
            "",
            f"- cv_tau (per mission, n>=2): `{legacy.fmt(tau_cv_mission)}`",
            f"- cv_tau (leave-out bootstrap): `{legacy.fmt(tau_cv_leave)}`",
            f"- sign_consistency: `{legacy.fmt(sign_consistency)}`",
            f"- directionality: `{legacy.fmt(fit_p.directionality)}`",
        ],
    )

    run_log_lines = [
        "QNG trajectory REAL run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_id: {args.dataset_id}",
        f"flyby_csv: {flyby_csv}",
        f"use_pioneer_anchor: {args.use_pioneer_anchor}",
        f"pioneer_csv: {args.pioneer_csv}",
        f"flyby_pass_ids: {args.flyby_pass_ids}",
        f"pioneer_record_ids: {args.pioneer_record_ids}",
        f"amp_gate_mode: {args.amp_gate_mode}",
        f"amp_band_min: {legacy.fmt(amp_band_min)}",
        f"amp_band_max: {legacy.fmt(amp_band_max)}",
        f"n_control_runs: {args.n_control_runs}",
        f"leave_out_runs: {args.leave_out_runs}",
        f"seed: {args.seed}",
        f"science_rows: {len(science_perigee)}",
        f"control_rows: {len(control_obs)}",
        f"science_flyby_rows: {len(science_flyby)}",
        f"science_pioneer_rows: {len(science_pioneer)}",
        f"required_rules: {', '.join(required_rules)}",
        f"duration_seconds: {legacy.fmt(time.perf_counter() - t0)}",
        "",
    ]
    if manifest_row is not None:
        run_log_lines.extend(["dataset_manifest_entry:", json.dumps(manifest_row, ensure_ascii=False, indent=2), ""])
    if warnings:
        run_log_lines.append("warnings:")
        for w in warnings:
            run_log_lines.append(f"- {w}")
        run_log_lines.append("")
    write_md(out_dir / "run-log.txt", run_log_lines)

    print(
        f"QNG trajectory REAL run complete for {args.test_id}: "
        f"delta_chi2={legacy.fmt(fit_p.dchi2)} "
        f"delta_aic={legacy.fmt(fit_p.daic)} "
        f"delta_bic={legacy.fmt(fit_p.dbic)} "
        f"tau_fit={legacy.fmt(fit_p.tau)} "
        f"pass={recommendation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
