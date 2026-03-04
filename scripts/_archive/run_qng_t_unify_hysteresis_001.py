#!/usr/bin/env python3
"""
QNG-T-UNIFY-001 + QNG-T-HYST-001

1) One-parameter law:
   Fit a single global lambda on lensing + rotation simultaneously.

2) Hysteresis proxy check:
   Split lensing sample into low-offset (relaxed-like) and high-offset
   (merging-like) subsets and test whether the same locked lambda captures
   the offset-dispersion contrast without introducing new parameters.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import math
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LENSING_CSV = ROOT / "data" / "lensing" / "lensing_ds006_hybrid.csv"
DEFAULT_ROTATION_CSV = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-unify-001"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0.0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_key_value_csv(path: Path, payload: dict[str, str]) -> None:
    write_csv(path, ["metric", "value"], [{"metric": k, "value": v} for k, v in payload.items()])


def write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-UNIFY-001 and QNG-T-HYST-001.")
    p.add_argument("--test-id-unify", default="QNG-T-UNIFY-001")
    p.add_argument("--test-id-hyst", default="QNG-T-HYST-001")
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--lensing-csv", default=str(DEFAULT_LENSING_CSV))
    p.add_argument("--rotation-csv", default=str(DEFAULT_ROTATION_CSV))
    p.add_argument("--lambda-max", type=float, default=4.0)
    p.add_argument("--grid-coarse", type=int, default=8000)
    p.add_argument("--grid-fine", type=int, default=6000)
    p.add_argument("--subset-fraction", type=float, default=0.25)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def fit_global_lambda(
    ld_module,
    lensing,
    rotation,
    lam_max: float,
    grid_coarse: int,
    grid_fine: int,
) -> tuple[float, float]:
    best_chi2 = float("inf")
    best_lam = 0.0

    n_coarse = max(1000, int(grid_coarse))
    for i in range(n_coarse + 1):
        lam = lam_max * i / n_coarse
        chi = ld_module.chi2_lensing(lensing, lam) + ld_module.chi2_rotation(rotation, lam)
        if chi < best_chi2:
            best_chi2 = chi
            best_lam = lam

    span = min(0.25 * lam_max, 0.2 + 0.2 * max(best_lam, 1.0))
    lo = max(0.0, best_lam - span)
    hi = min(lam_max, best_lam + span)
    n_fine = max(1000, int(grid_fine))
    for i in range(n_fine + 1):
        lam = lo + (hi - lo) * i / n_fine
        chi = ld_module.chi2_lensing(lensing, lam) + ld_module.chi2_rotation(rotation, lam)
        if chi < best_chi2:
            best_chi2 = chi
            best_lam = lam
    return best_lam, best_chi2


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.append(str((ROOT / "scripts").resolve()))
    import run_qng_t_027_lensing_dark as ld  # type: ignore

    t0 = time.perf_counter()
    warnings: list[str] = []

    lens_csv = Path(args.lensing_csv)
    if not lens_csv.is_absolute():
        lens_csv = (ROOT / lens_csv).resolve()
    rot_csv = Path(args.rotation_csv)
    if not rot_csv.is_absolute():
        rot_csv = (ROOT / rot_csv).resolve()

    lensing, lens_warnings = ld.parse_lensing_csv(lens_csv)
    rotation, rot_warnings = ld.parse_rotation_csv(rot_csv)
    warnings.extend(lens_warnings)
    warnings.extend(rot_warnings)

    lam, chi_one = fit_global_lambda(
        ld_module=ld,
        lensing=lensing,
        rotation=rotation,
        lam_max=max(0.5, float(args.lambda_max)),
        grid_coarse=args.grid_coarse,
        grid_fine=args.grid_fine,
    )

    chi0_l = ld.chi2_lensing(lensing, 0.0)
    chi0_r = ld.chi2_rotation(rotation, 0.0)
    chi0 = chi0_l + chi0_r
    chi1_l = ld.chi2_lensing(lensing, lam)
    chi1_r = ld.chi2_rotation(rotation, lam)
    chi1 = chi1_l + chi1_r

    n_total = len(lensing) + len(rotation)
    aic0 = ld.compute_aic(chi0, 0)
    bic0 = ld.compute_bic(chi0, 0, n_total)
    aic1 = ld.compute_aic(chi1, 1)
    bic1 = ld.compute_bic(chi1, 1, n_total)

    two_param = ld.evaluate_models(lensing, rotation)
    aic2 = ld.compute_aic(two_param.chi2_memory, 2)
    bic2 = ld.compute_bic(two_param.chi2_memory, 2, n_total)

    # Hysteresis proxy split (no new fit parameter).
    frac = min(max(args.subset_fraction, 0.10), 0.40)
    q_count = max(16, int(round(len(lensing) * frac)))
    q_count = min(q_count, len(lensing) // 2)
    if q_count < 8:
        raise RuntimeError("Too few lensing points for relaxed/merging subset split.")

    lens_offsets: list[tuple[int, float]] = []
    for i, p in enumerate(lensing):
        obs = math.hypot(p.obs_dx, p.obs_dy)
        lens_offsets.append((i, obs))
    lens_offsets.sort(key=lambda t: t[1])
    relaxed_ids = {i for i, _ in lens_offsets[:q_count]}
    merging_ids = {i for i, _ in lens_offsets[-q_count:]}

    subset_rows: list[dict[str, str]] = []
    relaxed_obs: list[float] = []
    relaxed_pred: list[float] = []
    merging_obs: list[float] = []
    merging_pred: list[float] = []

    for i, p in enumerate(lensing):
        obs = math.hypot(p.obs_dx, p.obs_dy)
        pred = math.hypot(lam * p.grad_dx, lam * p.grad_dy)
        resid = obs - pred
        if i in relaxed_ids:
            subset = "relaxed_like"
            relaxed_obs.append(obs)
            relaxed_pred.append(pred)
        elif i in merging_ids:
            subset = "merging_like"
            merging_obs.append(obs)
            merging_pred.append(pred)
        else:
            subset = "middle"
        subset_rows.append(
            {
                "system_id": p.system_id,
                "subset": subset,
                "obs_offset": fmt(obs),
                "pred_offset": fmt(pred),
                "abs_residual": fmt(abs(resid)),
            }
        )

    relaxed_obs_med = statistics.median(relaxed_obs)
    relaxed_pred_med = statistics.median(relaxed_pred)
    merging_obs_med = statistics.median(merging_obs)
    merging_pred_med = statistics.median(merging_pred)
    relaxed_obs_std = statistics.pstdev(relaxed_obs)
    relaxed_pred_std = statistics.pstdev(relaxed_pred)
    merging_obs_std = statistics.pstdev(merging_obs)
    merging_pred_std = statistics.pstdev(merging_pred)
    relaxed_mae = statistics.fmean(abs(a - b) for a, b in zip(relaxed_obs, relaxed_pred))
    merging_mae = statistics.fmean(abs(a - b) for a, b in zip(merging_obs, merging_pred))

    disp_ratio_obs = merging_obs_std / max(relaxed_obs_std, 1e-30)
    disp_ratio_pred = merging_pred_std / max(relaxed_pred_std, 1e-30)
    dispersion_alignment_log = abs(math.log(max(disp_ratio_obs, 1e-30) / max(disp_ratio_pred, 1e-30)))

    gates = {
        "U1_delta_chi2": (chi1 - chi0) < 0.0,
        "U2_delta_aic": (aic1 - aic0) <= -10.0,
        "U3_delta_bic": (bic1 - bic0) <= -10.0,
        "U4_one_param_competitiveness": (aic1 - aic2) <= 2.5,
        "H1_subset_separation_obs": merging_obs_med > relaxed_obs_med,
        "H2_subset_separation_pred": merging_pred_med > relaxed_pred_med,
        "H3_dispersion_alignment": dispersion_alignment_log <= 0.20,
        "H4_no_new_params": True,
    }
    decision = "pass" if all(gates.values()) else "fail"

    write_key_value_csv(
        out_dir / "fit-summary.csv",
        {
            "test_id_unify": args.test_id_unify,
            "test_id_hyst": args.test_id_hyst,
            "dataset_id": args.dataset_id,
            "decision": decision,
            "n_lensing": str(len(lensing)),
            "n_rotation": str(len(rotation)),
            "lambda_global": fmt(lam),
            "chi2_baseline": fmt(chi0),
            "chi2_one_param": fmt(chi1),
            "chi2_two_param": fmt(two_param.chi2_memory),
            "delta_chi2_one_vs_base": fmt(chi1 - chi0),
            "delta_aic_one_vs_base": fmt(aic1 - aic0),
            "delta_bic_one_vs_base": fmt(bic1 - bic0),
            "delta_chi2_one_vs_two": fmt(chi1 - two_param.chi2_memory),
            "delta_aic_one_vs_two": fmt(aic1 - aic2),
            "delta_bic_one_vs_two": fmt(bic1 - bic2),
            "relaxed_obs_median": fmt(relaxed_obs_med),
            "merging_obs_median": fmt(merging_obs_med),
            "relaxed_pred_median": fmt(relaxed_pred_med),
            "merging_pred_median": fmt(merging_pred_med),
            "dispersion_ratio_obs": fmt(disp_ratio_obs),
            "dispersion_ratio_pred": fmt(disp_ratio_pred),
            "dispersion_alignment_log": fmt(dispersion_alignment_log),
            "relaxed_mae": fmt(relaxed_mae),
            "merging_mae": fmt(merging_mae),
            "rule_pass_U1_delta_chi2": str(gates["U1_delta_chi2"]),
            "rule_pass_U2_delta_aic": str(gates["U2_delta_aic"]),
            "rule_pass_U3_delta_bic": str(gates["U3_delta_bic"]),
            "rule_pass_U4_one_param_competitiveness": str(gates["U4_one_param_competitiveness"]),
            "rule_pass_H1_subset_separation_obs": str(gates["H1_subset_separation_obs"]),
            "rule_pass_H2_subset_separation_pred": str(gates["H2_subset_separation_pred"]),
            "rule_pass_H3_dispersion_alignment": str(gates["H3_dispersion_alignment"]),
            "rule_pass_H4_no_new_params": str(gates["H4_no_new_params"]),
        },
    )

    write_csv(
        out_dir / "one_parameter_comparison.csv",
        ["model", "n_params", "chi2_total", "aic_total", "bic_total"],
        [
            {
                "model": "baseline_lambda0",
                "n_params": "0",
                "chi2_total": fmt(chi0),
                "aic_total": fmt(aic0),
                "bic_total": fmt(bic0),
            },
            {
                "model": "one_param_global_lambda",
                "n_params": "1",
                "chi2_total": fmt(chi1),
                "aic_total": fmt(aic1),
                "bic_total": fmt(bic1),
            },
            {
                "model": "two_param_reference_tau_plus_k",
                "n_params": "2",
                "chi2_total": fmt(two_param.chi2_memory),
                "aic_total": fmt(aic2),
                "bic_total": fmt(bic2),
            },
        ],
    )

    write_key_value_csv(
        out_dir / "hysteresis_summary.csv",
        {
            "subset_fraction": fmt(frac),
            "subset_count_each": str(q_count),
            "relaxed_obs_median": fmt(relaxed_obs_med),
            "merging_obs_median": fmt(merging_obs_med),
            "relaxed_pred_median": fmt(relaxed_pred_med),
            "merging_pred_median": fmt(merging_pred_med),
            "relaxed_obs_std": fmt(relaxed_obs_std),
            "merging_obs_std": fmt(merging_obs_std),
            "relaxed_pred_std": fmt(relaxed_pred_std),
            "merging_pred_std": fmt(merging_pred_std),
            "dispersion_ratio_obs": fmt(disp_ratio_obs),
            "dispersion_ratio_pred": fmt(disp_ratio_pred),
            "dispersion_alignment_log": fmt(dispersion_alignment_log),
            "relaxed_mae": fmt(relaxed_mae),
            "merging_mae": fmt(merging_mae),
        },
    )

    write_csv(out_dir / "subset_assignments.csv", list(subset_rows[0].keys()), subset_rows)

    write_md(
        out_dir / "run-summary.md",
        [
            "# Unified Law + Hysteresis Summary",
            "",
            f"- decision: `{decision}`",
            f"- lambda_global: `{fmt(lam)}`",
            f"- delta_chi2 (one vs baseline): `{fmt(chi1 - chi0)}`",
            f"- delta_aic (one vs baseline): `{fmt(aic1 - aic0)}`",
            f"- delta_bic (one vs baseline): `{fmt(bic1 - bic0)}`",
            f"- delta_aic (one vs two-param): `{fmt(aic1 - aic2)}`",
            "",
            "## Hysteresis proxy",
            f"- relaxed_obs_median: `{fmt(relaxed_obs_med)}`",
            f"- merging_obs_median: `{fmt(merging_obs_med)}`",
            f"- relaxed_pred_median: `{fmt(relaxed_pred_med)}`",
            f"- merging_pred_median: `{fmt(merging_pred_med)}`",
            f"- dispersion_alignment_log: `{fmt(dispersion_alignment_log)}`",
            "",
            "## Gates",
            f"- U1 delta_chi2: `{'pass' if gates['U1_delta_chi2'] else 'fail'}`",
            f"- U2 delta_aic: `{'pass' if gates['U2_delta_aic'] else 'fail'}`",
            f"- U3 delta_bic: `{'pass' if gates['U3_delta_bic'] else 'fail'}`",
            f"- U4 one-param competitiveness: `{'pass' if gates['U4_one_param_competitiveness'] else 'fail'}`",
            f"- H1 subset separation obs: `{'pass' if gates['H1_subset_separation_obs'] else 'fail'}`",
            f"- H2 subset separation pred: `{'pass' if gates['H2_subset_separation_pred'] else 'fail'}`",
            f"- H3 dispersion alignment: `{'pass' if gates['H3_dispersion_alignment'] else 'fail'}`",
            f"- H4 no new params: `{'pass' if gates['H4_no_new_params'] else 'fail'}`",
        ],
    )

    run_log = [
        "QNG-T-UNIFY-001 + QNG-T-HYST-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id_unify: {args.test_id_unify}",
        f"test_id_hyst: {args.test_id_hyst}",
        f"dataset_id: {args.dataset_id}",
        f"lensing_csv: {lens_csv}",
        f"rotation_csv: {rot_csv}",
        f"lambda_max: {args.lambda_max}",
        f"grid_coarse: {args.grid_coarse}",
        f"grid_fine: {args.grid_fine}",
        f"subset_fraction: {fmt(frac)}",
        f"duration_seconds: {fmt(time.perf_counter() - t0)}",
        f"decision: {decision}",
        "",
    ]
    if warnings:
        run_log.append("warnings:")
        for w in warnings:
            run_log.append(f"- {w}")
    write_md(out_dir / "run-log.txt", run_log)

    print(
        f"QNG unify+hysteresis run complete: decision={decision} "
        f"lambda={fmt(lam)} dchi2={fmt(chi1 - chi0)} "
        f"daic={fmt(aic1 - aic0)} dbic={fmt(bic1 - bic0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

