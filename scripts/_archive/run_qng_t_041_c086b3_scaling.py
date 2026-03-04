#!/usr/bin/env python3
"""
Executable scaling-law audit for QNG C-086b3 amplitude branch.

Goals:
- replace rigid fixed band with a covariate-dependent amplitude model
- keep prereg + out-of-sample holdout workflow
- provide explicit uncertainty and systematic-control diagnostics

Dependency policy: stdlib only
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import json
import math
import statistics
import time

import run_qng_t_028_trajectory as legacy


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FLYBY_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-041-c086b3-scaling"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"

MU_EARTH = 3.986004418e14
R_EARTH_KM = 6378.1363


@dataclass
class FlybyRow:
    pass_id: str
    mission_id: str
    trajectory_class: str
    source_ref: str
    r_perigee_km: float
    v_inf_km_s: float
    delta_in_deg: float
    delta_out_deg: float
    delta_v_obs_mm_s: float
    delta_v_sigma_mm_s: float
    thermal_corr_mm_s: float
    srp_corr_mm_s: float
    maneuver_corr_mm_s: float
    drag_corr_mm_s: float

    # Derived covariates/targets
    altitude_km: float
    v_perigee_m_s: float
    grad_g_proxy: float
    geom_proxy: float
    non_grav_proxy_m_s2: float
    amp_obs_m_s2: float
    sigma_amp_m_s2: float
    is_control: bool


def parse_id_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


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


def parse_flyby_csv(path: Path) -> tuple[list[FlybyRow], list[str]]:
    warnings: list[str] = []
    out: list[FlybyRow] = []
    required = {
        "pass_id",
        "mission_id",
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
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing flyby columns: {', '.join(missing)}")

        for row in reader:
            try:
                r_km = float(str(row["r_perigee_km"]).replace(",", ""))
                v_inf_km_s = float(str(row["v_inf_km_s"]).replace(",", ""))
                d_in = float(str(row["delta_in_deg"]).replace(",", ""))
                d_out = float(str(row["delta_out_deg"]).replace(",", ""))
                dv_obs = float(str(row["delta_v_obs_mm_s"]).replace(",", ""))
                dv_sig = max(1e-6, float(str(row["delta_v_sigma_mm_s"]).replace(",", "")))
                c_th = float(str(row["thermal_corr_mm_s"]).replace(",", ""))
                c_srp = float(str(row["srp_corr_mm_s"]).replace(",", ""))
                c_man = float(str(row["maneuver_corr_mm_s"]).replace(",", ""))
                c_drag = float(str(row["drag_corr_mm_s"]).replace(",", ""))
            except Exception:
                warnings.append(f"Skipping malformed row: {row.get('pass_id', 'unknown')}")
                continue

            rp_m = r_km * 1000.0
            v_inf_m_s = v_inf_km_s * 1000.0
            v_perigee = math.sqrt(v_inf_m_s * v_inf_m_s + 2.0 * MU_EARTH / max(rp_m, 1e-12))
            t_peri = rp_m / max(v_perigee, 1e-12)
            delta_cos = math.cos(math.radians(d_in)) - math.cos(math.radians(d_out))
            grad_g = MU_EARTH / max(rp_m ** 3, 1e-30)

            corr_mm_s = c_th + c_srp + c_man + c_drag
            dv_corr_mm_s = dv_obs - corr_mm_s
            a_obs = (dv_corr_mm_s * 1e-3) / max(t_peri, 1e-12)
            a_sig = (dv_sig * 1e-3) / max(t_peri, 1e-12)
            non_grav_proxy = abs(corr_mm_s * 1e-3) / max(t_peri, 1e-12)

            out.append(
                FlybyRow(
                    pass_id=str(row["pass_id"]).strip(),
                    mission_id=str(row["mission_id"]).strip(),
                    trajectory_class=str(row["trajectory_class"]).strip(),
                    source_ref=str(row["source_ref"]).strip(),
                    r_perigee_km=r_km,
                    v_inf_km_s=v_inf_km_s,
                    delta_in_deg=d_in,
                    delta_out_deg=d_out,
                    delta_v_obs_mm_s=dv_obs,
                    delta_v_sigma_mm_s=dv_sig,
                    thermal_corr_mm_s=c_th,
                    srp_corr_mm_s=c_srp,
                    maneuver_corr_mm_s=c_man,
                    drag_corr_mm_s=c_drag,
                    altitude_km=max(r_km - R_EARTH_KM, 1e-6),
                    v_perigee_m_s=v_perigee,
                    grad_g_proxy=abs(grad_g),
                    geom_proxy=abs(delta_cos),
                    non_grav_proxy_m_s2=non_grav_proxy,
                    amp_obs_m_s2=abs(a_obs),
                    sigma_amp_m_s2=max(a_sig, 1e-14),
                    is_control=("control" in str(row["trajectory_class"]).lower()),
                )
            )

    if not out:
        raise ValueError("No usable rows found in flyby CSV.")
    return out, warnings


def build_feature_refs(rows: list[FlybyRow]) -> dict[str, float]:
    v0 = statistics.median([r.v_perigee_m_s for r in rows])
    h0 = statistics.median([r.altitude_km for r in rows])
    g0 = statistics.median([r.grad_g_proxy for r in rows])
    ng_vals = [r.non_grav_proxy_m_s2 for r in rows if r.non_grav_proxy_m_s2 > 0.0]
    ng0 = statistics.median(ng_vals) if ng_vals else 1e-12
    return {
        "v0": max(v0, 1e-12),
        "h0": max(h0, 1e-6),
        "g0": max(g0, 1e-30),
        "ng0": max(ng0, 1e-12),
        "eps_amp": 1e-12,
    }


def design_vector(row: FlybyRow, refs: dict[str, float]) -> list[float]:
    x_v = math.log(max(row.v_perigee_m_s / refs["v0"], 1e-18))
    x_h = math.log(max((row.altitude_km + refs["h0"]) / refs["h0"], 1e-18))
    x_g = math.log(max(row.grad_g_proxy / refs["g0"], 1e-30))
    x_geom = math.log(1.0 + max(row.geom_proxy, 0.0))
    x_ng = math.log(1.0 + max(row.non_grav_proxy_m_s2 / refs["ng0"], 0.0))
    return [1.0, x_v, x_h, x_g, x_geom, x_ng]


def weighted_normal_equations(
    x_mat: list[list[float]],
    y_vec: list[float],
    w_vec: list[float],
    ridge_lambda: float,
) -> tuple[list[list[float]], list[float]]:
    p = len(x_mat[0])
    a = [[0.0 for _ in range(p)] for _ in range(p)]
    b = [0.0 for _ in range(p)]
    for x, y, w in zip(x_mat, y_vec, w_vec):
        for i in range(p):
            b[i] += w * x[i] * y
            for j in range(p):
                a[i][j] += w * x[i] * x[j]
    for i in range(p):
        a[i][i] += ridge_lambda
    return a, b


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-18:
            raise ValueError("Singular normal-equation matrix.")
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return [m[i][n] for i in range(n)]


def invert_matrix(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-18:
            raise ValueError("Singular matrix in inversion.")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        for j in range(2 * n):
            aug[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0.0:
                continue
            for j in range(2 * n):
                aug[r][j] -= factor * aug[col][j]
    return [row[n:] for row in aug]


def predict_log_amp(rows: list[FlybyRow], beta: list[float], refs: dict[str, float]) -> list[float]:
    preds: list[float] = []
    for row in rows:
        x = design_vector(row, refs)
        preds.append(sum(b * xi for b, xi in zip(beta, x)))
    return preds


def evaluate_rows(
    rows: list[FlybyRow],
    beta: list[float],
    refs: dict[str, float],
    sigma_log_cal: float,
) -> tuple[dict[str, float], list[dict[str, str]], list[float]]:
    if not rows:
        return (
            {
                "n": 0.0,
                "mae_log": float("nan"),
                "rmse_log": float("nan"),
                "median_ratio": float("nan"),
                "mape_pct": float("nan"),
                "coverage_95": float("nan"),
            },
            [],
            [],
        )
    y_true_log = [math.log(r.amp_obs_m_s2 + refs["eps_amp"]) for r in rows]
    y_hat_log = predict_log_amp(rows, beta, refs)
    err = [yh - yt for yh, yt in zip(y_hat_log, y_true_log)]
    abs_err = [abs(v) for v in err]
    rmse = math.sqrt(statistics.fmean([v * v for v in err]))
    ratios = [math.exp(yh) / max(math.exp(yt), 1e-30) for yh, yt in zip(y_hat_log, y_true_log)]
    mape = 100.0 * statistics.fmean([abs(r - 1.0) for r in ratios])
    lo = [yh - 1.96 * sigma_log_cal for yh in y_hat_log]
    hi = [yh + 1.96 * sigma_log_cal for yh in y_hat_log]
    covered = sum(1 for yt, l, h in zip(y_true_log, lo, hi) if (yt >= l and yt <= h))
    coverage = covered / max(1, len(rows))

    table: list[dict[str, str]] = []
    for row, yt, yh in zip(rows, y_true_log, y_hat_log):
        table.append(
            {
                "pass_id": row.pass_id,
                "mission_id": row.mission_id,
                "trajectory_class": row.trajectory_class,
                "amp_obs_m_s2": legacy.fmt(math.exp(yt)),
                "amp_pred_m_s2": legacy.fmt(max(math.exp(yh) - refs["eps_amp"], 0.0)),
                "log_error": legacy.fmt(yh - yt),
                "ratio_pred_over_obs": legacy.fmt(math.exp(yh) / max(math.exp(yt), 1e-30)),
                "altitude_km": legacy.fmt(row.altitude_km),
                "v_perigee_m_s": legacy.fmt(row.v_perigee_m_s),
                "grad_g_proxy": legacy.fmt(row.grad_g_proxy),
                "geom_proxy": legacy.fmt(row.geom_proxy),
                "non_grav_proxy_m_s2": legacy.fmt(row.non_grav_proxy_m_s2),
                "is_control": str(row.is_control),
            }
        )

    return (
        {
            "n": float(len(rows)),
            "mae_log": statistics.fmean(abs_err),
            "rmse_log": rmse,
            "median_ratio": statistics.median(ratios),
            "mape_pct": mape,
            "coverage_95": coverage,
        },
        table,
        y_hat_log,
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG C-086b3 scaling-law audit.")
    p.add_argument("--test-id", default="QNG-T-041")
    p.add_argument("--dataset-id", default="DS-005")
    p.add_argument("--flyby-csv", default=str(DEFAULT_FLYBY_CSV))
    p.add_argument("--calibration-pass-ids", default="", help="Optional explicit calibration pass IDs.")
    p.add_argument(
        "--holdout-pass-ids",
        default="JUNO_1,BEPICOLOMBO_1,SOLAR_ORBITER_1",
        help="Comma-separated holdout pass IDs (locked, append-only policy).",
    )
    p.add_argument("--ridge-lambda", type=float, default=1e-6)
    p.add_argument("--max-holdout-rmse-log", type=float, default=1.25)
    p.add_argument("--max-holdout-mae-log", type=float, default=1.00)
    p.add_argument("--min-holdout-median-ratio", type=float, default=0.50)
    p.add_argument("--max-holdout-median-ratio", type=float, default=2.00)
    p.add_argument("--min-holdout-n", type=int, default=3)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    t0 = time.perf_counter()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    manifest_row = read_manifest(args.dataset_id)
    if manifest_row is None:
        warnings.append(f"Dataset id '{args.dataset_id}' not found in dataset-manifest.json")

    flyby_csv = Path(args.flyby_csv)
    if not flyby_csv.is_absolute():
        flyby_csv = (ROOT / flyby_csv).resolve()
    rows, parse_warnings = parse_flyby_csv(flyby_csv)
    warnings.extend(parse_warnings)

    holdout_ids = parse_id_list(args.holdout_pass_ids)
    calib_ids = parse_id_list(args.calibration_pass_ids)
    if not holdout_ids:
        raise ValueError("holdout-pass-ids must contain at least one pass_id")

    row_by_id = {r.pass_id: r for r in rows}
    missing_holdout_ids = sorted([pid for pid in holdout_ids if pid not in row_by_id])
    if missing_holdout_ids:
        warnings.append(f"Missing holdout pass_id rows: {', '.join(missing_holdout_ids)}")

    if calib_ids:
        calibration_rows = [r for r in rows if r.pass_id in set(calib_ids)]
        missing_calib_ids = sorted([pid for pid in calib_ids if pid not in row_by_id])
        if missing_calib_ids:
            warnings.append(f"Missing calibration pass_id rows: {', '.join(missing_calib_ids)}")
    else:
        holdout_set = set(holdout_ids)
        calibration_rows = [r for r in rows if r.pass_id not in holdout_set]

    holdout_rows = [r for r in rows if r.pass_id in set(holdout_ids)]
    if len(calibration_rows) < 6:
        raise ValueError("Need at least 6 calibration rows for C-086b3 scaling fit.")

    refs = build_feature_refs(calibration_rows)
    x_mat = [design_vector(r, refs) for r in calibration_rows]
    y_vec = [math.log(r.amp_obs_m_s2 + refs["eps_amp"]) for r in calibration_rows]
    w_vec = [1.0 / max(r.sigma_amp_m_s2 * r.sigma_amp_m_s2, 1e-30) for r in calibration_rows]

    normal_a, normal_b = weighted_normal_equations(x_mat, y_vec, w_vec, args.ridge_lambda)
    beta = solve_linear_system(normal_a, normal_b)

    cal_metrics, cal_table, yhat_cal = evaluate_rows(calibration_rows, beta, refs, sigma_log_cal=0.0)
    cal_errors = [yh - yt for yh, yt in zip(yhat_cal, y_vec)]
    p = len(beta)
    n = len(cal_errors)
    sse = sum(e * e for e in cal_errors)
    dof = max(1, n - p)
    sigma_log_cal = math.sqrt(sse / dof)

    hold_metrics, hold_table, _ = evaluate_rows(holdout_rows, beta, refs, sigma_log_cal=sigma_log_cal)
    cal_metrics["coverage_95"] = float("nan")

    inv_a = invert_matrix(normal_a)
    cov = [[sigma_log_cal * sigma_log_cal * v for v in row] for row in inv_a]
    se = [math.sqrt(max(cov[i][i], 0.0)) for i in range(len(beta))]

    if missing_holdout_ids:
        holdout_status = "blocked_missing_holdout_rows"
    elif int(hold_metrics["n"]) < args.min_holdout_n:
        holdout_status = "blocked_insufficient_holdout_n"
    else:
        gate_rmse = hold_metrics["rmse_log"] <= args.max_holdout_rmse_log
        gate_mae = hold_metrics["mae_log"] <= args.max_holdout_mae_log
        gate_ratio = args.min_holdout_median_ratio <= hold_metrics["median_ratio"] <= args.max_holdout_median_ratio
        holdout_status = "pass" if (gate_rmse and gate_mae and gate_ratio) else "fail"

    coef_rows: list[dict[str, str]] = []
    coef_names = ["intercept", "log_v_perigee", "log_altitude", "log_grad_g_proxy", "log_geom_proxy", "log_non_grav_proxy"]
    for name, b, s in zip(coef_names, beta, se):
        coef_rows.append({"coefficient": name, "beta": legacy.fmt(b), "std_error": legacy.fmt(s), "z_approx": legacy.fmt(b / max(s, 1e-18))})

    write_csv(
        out_dir / "calibration-predictions.csv",
        fieldnames=list(cal_table[0].keys()) if cal_table else [
            "pass_id",
            "mission_id",
            "trajectory_class",
            "amp_obs_m_s2",
            "amp_pred_m_s2",
            "log_error",
            "ratio_pred_over_obs",
            "altitude_km",
            "v_perigee_m_s",
            "grad_g_proxy",
            "geom_proxy",
            "non_grav_proxy_m_s2",
            "is_control",
        ],
        rows=cal_table,
    )
    write_csv(
        out_dir / "holdout-predictions.csv",
        fieldnames=list(hold_table[0].keys()) if hold_table else [
            "pass_id",
            "mission_id",
            "trajectory_class",
            "amp_obs_m_s2",
            "amp_pred_m_s2",
            "log_error",
            "ratio_pred_over_obs",
            "altitude_km",
            "v_perigee_m_s",
            "grad_g_proxy",
            "geom_proxy",
            "non_grav_proxy_m_s2",
            "is_control",
        ],
        rows=hold_table,
    )
    write_csv(out_dir / "coefficients.csv", fieldnames=["coefficient", "beta", "std_error", "z_approx"], rows=coef_rows)

    # Simple line chart: observed vs predicted amplitudes sorted by observed.
    cal_sorted = sorted(cal_table, key=lambda r: float(r["amp_obs_m_s2"]))
    if cal_sorted:
        xs = [float(i + 1) for i in range(len(cal_sorted))]
        y_obs = [float(r["amp_obs_m_s2"]) for r in cal_sorted]
        y_pred = [float(r["amp_pred_m_s2"]) for r in cal_sorted]
        legacy.plot_series_png(
            out_dir / "scaling-fit-calibration.png",
            xs,
            [
                ("obs_amp", y_obs, (35, 97, 185)),
                ("pred_amp", y_pred, (22, 148, 112)),
            ],
        )

    summary = {
        "test_id": args.test_id,
        "dataset_id": args.dataset_id,
        "model_id": "C-086b3-scaling-v1",
        "data_source_mode": "real_published_flyby",
        "n_total_rows": str(len(rows)),
        "n_calibration": str(len(calibration_rows)),
        "n_holdout": str(len(holdout_rows)),
        "missing_holdout_ids": ",".join(missing_holdout_ids),
        "holdout_status": holdout_status,
        "calibration_mae_log": legacy.fmt(cal_metrics["mae_log"]),
        "calibration_rmse_log": legacy.fmt(cal_metrics["rmse_log"]),
        "calibration_median_ratio": legacy.fmt(cal_metrics["median_ratio"]),
        "calibration_mape_pct": legacy.fmt(cal_metrics["mape_pct"]),
        "sigma_log_cal": legacy.fmt(sigma_log_cal),
        "holdout_mae_log": legacy.fmt(hold_metrics["mae_log"]),
        "holdout_rmse_log": legacy.fmt(hold_metrics["rmse_log"]),
        "holdout_median_ratio": legacy.fmt(hold_metrics["median_ratio"]),
        "holdout_mape_pct": legacy.fmt(hold_metrics["mape_pct"]),
        "holdout_coverage_95": legacy.fmt(hold_metrics["coverage_95"]),
        "gate_max_holdout_rmse_log": legacy.fmt(args.max_holdout_rmse_log),
        "gate_max_holdout_mae_log": legacy.fmt(args.max_holdout_mae_log),
        "gate_ratio_min": legacy.fmt(args.min_holdout_median_ratio),
        "gate_ratio_max": legacy.fmt(args.max_holdout_median_ratio),
        "gate_min_holdout_n": str(args.min_holdout_n),
        "v0_ref_m_s": legacy.fmt(refs["v0"]),
        "h0_ref_km": legacy.fmt(refs["h0"]),
        "g0_ref": legacy.fmt(refs["g0"]),
        "ng0_ref_m_s2": legacy.fmt(refs["ng0"]),
        "ridge_lambda": legacy.fmt(args.ridge_lambda),
        "pass_recommendation": "pass" if holdout_status == "pass" else ("blocked" if holdout_status.startswith("blocked_") else "fail"),
    }
    legacy.write_csv_dict(out_dir / "fit-summary.csv", summary)

    model_md = [
        "# C-086b3 Scaling Audit",
        "",
        "## Model Form",
        "",
        "```text",
        "log(A_obs + eps) = b0 + b1*log(v_p/v0) + b2*log((h_p+h0)/h0) + b3*log(|grad_g|/g0) + b4*log(1+geom) + b5*log(1+non_grav/ng0) + e",
        "```",
        "",
        "## Covariates",
        "",
        "- `h_p`: perigee altitude (`r_perigee_km - R_earth_km`)",
        "- `v_p`: perigee speed from hyperbolic-energy closure",
        "- `|grad_g|` proxy: `mu_earth / r_perigee^3`",
        "- `geom`: `|cos(delta_in)-cos(delta_out)|`",
        "- `non_grav`: acceleration-equivalent from explicit correction columns (thermal/SRP/maneuver/drag)",
        "",
        "## Split",
        "",
        f"- calibration rows: `{len(calibration_rows)}`",
        f"- holdout rows present: `{len(holdout_rows)}`",
        f"- missing holdout IDs: `{', '.join(missing_holdout_ids) if missing_holdout_ids else 'none'}`",
        f"- holdout status: `{holdout_status}`",
        "",
        "## Metrics",
        "",
        f"- calibration rmse_log: `{legacy.fmt(cal_metrics['rmse_log'])}`",
        f"- holdout rmse_log: `{legacy.fmt(hold_metrics['rmse_log'])}`",
        f"- holdout median_ratio: `{legacy.fmt(hold_metrics['median_ratio'])}`",
        f"- holdout coverage_95: `{legacy.fmt(hold_metrics['coverage_95'])}`",
        "",
        "## Coefficients",
        "",
        "| term | beta | std_error |",
        "| --- | --- | --- |",
    ]
    for row in coef_rows:
        model_md.append(f"| `{row['coefficient']}` | `{row['beta']}` | `{row['std_error']}` |")
    model_md.append("")
    (out_dir / "scaling-model.md").write_text("\n".join(model_md).rstrip() + "\n", encoding="utf-8")

    run_log = [
        "QNG C-086b3 scaling run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_id: {args.dataset_id}",
        f"flyby_csv: {flyby_csv}",
        f"calibration_pass_ids: {args.calibration_pass_ids}",
        f"holdout_pass_ids: {args.holdout_pass_ids}",
        f"ridge_lambda: {legacy.fmt(args.ridge_lambda)}",
        f"n_total_rows: {len(rows)}",
        f"n_calibration: {len(calibration_rows)}",
        f"n_holdout: {len(holdout_rows)}",
        f"holdout_status: {holdout_status}",
        f"duration_seconds: {time.perf_counter() - t0:.6f}",
        "",
        "dataset_manifest_entry:",
        json.dumps(manifest_row, indent=2) if manifest_row else "null",
        "",
        "warnings:",
    ]
    if warnings:
        run_log.extend([f"- {w}" for w in warnings])
    else:
        run_log.append("- none")
    (out_dir / "run-log.txt").write_text("\n".join(run_log).rstrip() + "\n", encoding="utf-8")

    print(
        "QNG C-086b3 scaling run complete: "
        f"holdout_status={holdout_status} "
        f"cal_rmse_log={legacy.fmt(cal_metrics['rmse_log'])} "
        f"hold_rmse_log={legacy.fmt(hold_metrics['rmse_log'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

