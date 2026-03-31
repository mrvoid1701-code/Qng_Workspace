#!/usr/bin/env python3
"""
QNG-T-STRATON-002: mass-scaling tau test on classic subset (published residuals only).
Authored by: Claude Sonnet 4.6 (2026-02-22).

Changes vs v1:
- Filtered to CLASSIC_PASS_IDS (no placeholder residuals).
- Gate 4: exact leave-one-row-out (all 13 individual fits).
- LOO influence diagnostics per-row (D1) and per-mission (D2).
- BIC decomposition: n, k, LL_model, LL_null, BIC_model, BIC_null explicitly logged.
- Sigma summary (min/median/max) logged to catch arbitrary-sigma inflation.
- Residual diagnostic (D4): raw residual + standardized residual vs mass for both models.
- Model C power-law: grid search (locked) + ternary search continuous cross-check.
- Model C: bootstrap 95% CI on best_beta.

Outputs (out_dir default: 05_validation/evidence/artifacts/qng-t-straton-002):
- fit-summary.csv          (gates + full BIC decomposition + sigma summary)
- bic-decomposition.csv    (n, k, LL, BIC, delta_LL, delta_BIC per model)
- residuals-diagnostic.csv (per-row: residual_A, residual_B, std_residual_A, std_residual_B, mass)
- loo-row-influence.csv
- loo-mission-influence.csv
- model-c-report.csv
- model-c-grid.csv
- bootstrap-alpha.csv
- bootstrap-beta-modelc.csv
- negative-controls-summary.csv
- straton-002-report.md
- run-log.txt
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

CLASSIC_PASS_IDS = {
    "GALILEO_1", "GALILEO_2",
    "NEAR_1",
    "CASSINI_1",
    "ROSETTA_1", "ROSETTA_2", "ROSETTA_3",
    "MESSENGER_1",
    "EPOXI_1", "EPOXI_2", "EPOXI_3", "EPOXI_4", "EPOXI_5",
}

BETA_GRID = [round(0.10 + i * 0.05, 4) for i in range(int((3.00 - 0.10) / 0.05) + 1)]
LOG_2PI = math.log(2.0 * math.pi)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(derived_path: Path, base_path: Path) -> pd.DataFrame:
    derived = pd.read_csv(derived_path)
    base = pd.read_csv(base_path)
    if "spacecraft_mass_kg" not in base.columns:
        raise ValueError("spacecraft_mass_kg column missing in base dataset")
    mass_map = dict(zip(base["pass_id"], base["spacecraft_mass_kg"]))
    derived["spacecraft_mass_kg"] = derived["pass_id"].map(mass_map)
    missing = derived["spacecraft_mass_kg"].isna().sum()
    if missing > 0:
        raise ValueError(f"missing mass entries: {missing}")
    before = len(derived)
    derived = derived[derived["pass_id"].isin(CLASSIC_PASS_IDS)].reset_index(drop=True)
    after = len(derived)
    print(f"[filter] {before} rows -> {after} classic rows ({before - after} excluded)")
    if after < 5:
        raise ValueError(f"classic subset too small: {after} rows")
    return derived


def get_sigma(df: pd.DataFrame) -> pd.Series:
    sigma = df["sigma_whole_m_s2"].copy()
    mask_zero = sigma == 0
    if mask_zero.any() and "sigma_perigee_m_s2" in df.columns:
        sigma.loc[mask_zero] = df.loc[mask_zero, "sigma_perigee_m_s2"]
    sigma = sigma.replace(0, 1e-18)
    return sigma


# ---------------------------------------------------------------------------
# WLS helpers
# ---------------------------------------------------------------------------

def _wls_single_param(obs: pd.Series, feature_eff: pd.Series, sigma: pd.Series):
    """Fit: a_obs + param * feature_eff = 0, return (param, chi2)."""
    w = 1.0 / (sigma ** 2)
    num = -(w * feature_eff * obs).sum()
    den = (w * feature_eff ** 2).sum()
    if den <= 0:
        return 0.0, 0.0
    param = num / den
    chi2 = float((w * (obs + param * feature_eff) ** 2).sum())
    return float(param), chi2


def _full_ll(obs: pd.Series, feature_eff: pd.Series, sigma: pd.Series, param: float) -> float:
    """Full Gaussian log-likelihood (includes sigma terms, not just chi2)."""
    resid = obs + param * feature_eff
    ll = -0.5 * float((LOG_2PI + 2.0 * sigma.apply(math.log) + (resid / sigma) ** 2).sum())
    return ll


# ---------------------------------------------------------------------------
# FitResult with full BIC decomposition
# ---------------------------------------------------------------------------

@dataclass
class FitResult:
    # Model A (null)
    tau_const: float
    chi2_const: float
    ll_const: float
    bic_const: float          # -2*ll + k*ln(n), k=1
    # Model B (straton linear)
    alpha: float
    chi2_alpha: float
    ll_alpha: float
    bic_alpha: float          # -2*ll + k*ln(n), k=1
    # Comparison
    delta_bic: float          # bic_alpha - bic_const
    delta_ll: float           # ll_alpha - ll_const
    # Dataset
    n: int
    sigma_min: float
    sigma_median: float
    sigma_max: float


def fit_models(df: pd.DataFrame) -> FitResult:
    obs = df["a_obs_whole_m_s2"]
    feature = df["feature_base_m_s3"]
    sigma = get_sigma(df)
    n = len(df)

    tau_const, chi2_const = _wls_single_param(obs, feature, sigma)
    ll_const = _full_ll(obs, feature, sigma, tau_const)
    bic_const = -2.0 * ll_const + 1.0 * math.log(n)   # k=1

    feature_mass = feature * df["spacecraft_mass_kg"]
    alpha, chi2_alpha = _wls_single_param(obs, feature_mass, sigma)
    ll_alpha = _full_ll(obs, feature_mass, sigma, alpha)
    bic_alpha = -2.0 * ll_alpha + 1.0 * math.log(n)   # k=1

    return FitResult(
        tau_const=tau_const,
        chi2_const=chi2_const,
        ll_const=ll_const,
        bic_const=bic_const,
        alpha=alpha,
        chi2_alpha=chi2_alpha,
        ll_alpha=ll_alpha,
        bic_alpha=bic_alpha,
        delta_bic=bic_alpha - bic_const,
        delta_ll=ll_alpha - ll_const,
        n=n,
        sigma_min=float(sigma.min()),
        sigma_median=float(sigma.median()),
        sigma_max=float(sigma.max()),
    )


# ---------------------------------------------------------------------------
# Residuals diagnostic (D4)
# ---------------------------------------------------------------------------

def residuals_diagnostic(df: pd.DataFrame, fit: FitResult) -> List[dict]:
    """Per-row residuals for both models. Reveals if 1-2 points drive everything."""
    obs = df["a_obs_whole_m_s2"]
    feature = df["feature_base_m_s3"]
    sigma = get_sigma(df)
    mass = df["spacecraft_mass_kg"]

    resid_a = obs + fit.tau_const * feature
    resid_b = obs + fit.alpha * mass * feature
    std_resid_a = resid_a / sigma
    std_resid_b = resid_b / sigma

    records = []
    for i in range(len(df)):
        records.append({
            "pass_id": df.iloc[i]["pass_id"] if "pass_id" in df.columns else str(i),
            "mission_id": df.iloc[i]["mission_id"] if "mission_id" in df.columns else "",
            "mass_kg": float(mass.iloc[i]),
            "sigma": float(sigma.iloc[i]),
            "a_obs": float(obs.iloc[i]),
            "residual_A": float(resid_a.iloc[i]),
            "residual_B": float(resid_b.iloc[i]),
            "std_residual_A": float(std_resid_a.iloc[i]),
            "std_residual_B": float(std_resid_b.iloc[i]),
            "leverage_flag": abs(float(std_resid_b.iloc[i])) > 2.0,
        })
    return records


# ---------------------------------------------------------------------------
# Bootstrap alpha (Model B)
# ---------------------------------------------------------------------------

def bootstrap_alpha(df: pd.DataFrame, n_runs: int = 400, seed: int = 20260225) -> List[float]:
    rng = random.Random(seed)
    obs_arr = df["a_obs_whole_m_s2"].values
    feat_arr = df["feature_base_m_s3"].values
    mass_arr = df["spacecraft_mass_kg"].values
    sig_arr = get_sigma(df).values
    n = len(df)
    values = []
    for _ in range(n_runs):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        s_obs = pd.Series([obs_arr[i] for i in idx])
        s_feat = pd.Series([feat_arr[i] for i in idx])
        s_mass = pd.Series([mass_arr[i] for i in idx])
        s_sig = pd.Series([sig_arr[i] for i in idx])
        alpha, _ = _wls_single_param(s_obs, s_feat * s_mass, s_sig)
        values.append(alpha)
    return values


# ---------------------------------------------------------------------------
# Exact leave-one-row-out (gate 4 + influence diagnostic D1)
# ---------------------------------------------------------------------------

def loo_rows(df: pd.DataFrame) -> List[dict]:
    fit_full = fit_models(df)
    records = []
    for i in range(len(df)):
        subset = df.drop(index=df.index[i]).reset_index(drop=True)
        if len(subset) < 4:
            continue
        fit_loo = fit_models(subset)
        delta_alpha = fit_loo.alpha - fit_full.alpha
        rel = (delta_alpha / abs(fit_full.alpha) * 100) if fit_full.alpha != 0 else float("nan")
        records.append({
            "row_idx": i,
            "pass_id": df.iloc[i]["pass_id"] if "pass_id" in df.columns else str(i),
            "mission_id": df.iloc[i]["mission_id"] if "mission_id" in df.columns else "",
            "mass_kg": float(df.iloc[i]["spacecraft_mass_kg"]),
            "alpha_full": fit_full.alpha,
            "alpha_loo": fit_loo.alpha,
            "delta_alpha": delta_alpha,
            "delta_alpha_rel_pct": rel,
            "delta_bic_loo": fit_loo.delta_bic,
            "delta_ll_loo": fit_loo.delta_ll,
            "gate_pass": fit_loo.delta_bic <= -10,
        })
    return records


# ---------------------------------------------------------------------------
# Leave-one-mission-out (diagnostic D2)
# ---------------------------------------------------------------------------

def loo_missions(df: pd.DataFrame) -> List[dict]:
    fit_full = fit_models(df)
    missions = sorted(df["mission_id"].unique())
    records = []
    for mission in missions:
        subset = df[df["mission_id"] != mission].reset_index(drop=True)
        if len(subset) < 4:
            continue
        fit_loo = fit_models(subset)
        n_dropped = int((df["mission_id"] == mission).sum())
        delta_alpha = fit_loo.alpha - fit_full.alpha
        rel = (delta_alpha / abs(fit_full.alpha) * 100) if fit_full.alpha != 0 else float("nan")
        records.append({
            "mission_id": mission,
            "n_rows_dropped": n_dropped,
            "alpha_full": fit_full.alpha,
            "alpha_loo": fit_loo.alpha,
            "delta_alpha": delta_alpha,
            "delta_alpha_rel_pct": rel,
            "delta_bic_loo": fit_loo.delta_bic,
            "delta_ll_loo": fit_loo.delta_ll,
            "gate_pass": fit_loo.delta_bic <= -10,
        })
    return records


# ---------------------------------------------------------------------------
# Model C: power-law fit tau = alpha * m^beta
# ---------------------------------------------------------------------------

def _fit_power_law_beta(df: pd.DataFrame, beta: float):
    """For fixed beta, fit alpha (WLS) and return (alpha, chi2, ll)."""
    obs = df["a_obs_whole_m_s2"]
    feature = df["feature_base_m_s3"]
    sigma = get_sigma(df)
    feature_c = feature * (df["spacecraft_mass_kg"] ** beta)
    alpha, chi2 = _wls_single_param(obs, feature_c, sigma)
    ll = _full_ll(obs, feature_c, sigma, alpha)
    return alpha, chi2, ll


def _ternary_search_beta(df: pd.DataFrame, lo: float = 0.10, hi: float = 3.00,
                         tol: float = 1e-6, max_iter: int = 200) -> float:
    """Continuous optimum for beta via ternary search (no scipy needed)."""
    for _ in range(max_iter):
        if hi - lo < tol:
            break
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        _, chi2_m1, _ = _fit_power_law_beta(df, m1)
        _, chi2_m2, _ = _fit_power_law_beta(df, m2)
        if chi2_m1 < chi2_m2:
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2.0


def fit_power_law(df: pd.DataFrame, fit_ab: FitResult) -> dict:
    """Grid search + ternary search for Model C. Diagnostic only."""
    n = len(df)

    best_grid: Optional[dict] = None
    grid_rows = []
    for beta in BETA_GRID:
        alpha_c, chi2_c, ll_c = _fit_power_law_beta(df, beta)
        bic_c = -2.0 * ll_c + 2.0 * math.log(n)   # k=2
        grid_rows.append({"beta": beta, "alpha_c": alpha_c, "chi2_c": chi2_c,
                          "ll_c": ll_c, "bic_c": bic_c})
        if best_grid is None or chi2_c < best_grid["chi2_c"]:
            best_grid = {"beta": beta, "alpha_c": alpha_c, "chi2_c": chi2_c,
                         "ll_c": ll_c, "bic_c": bic_c}

    if best_grid is None:
        return {}

    # Continuous cross-check via ternary search
    beta_continuous = _ternary_search_beta(df)
    alpha_cont, chi2_cont, ll_cont = _fit_power_law_beta(df, beta_continuous)
    bic_cont = -2.0 * ll_cont + 2.0 * math.log(n)

    delta_bic_c_vs_a = best_grid["bic_c"] - fit_ab.bic_const
    delta_bic_c_vs_b = best_grid["bic_c"] - fit_ab.bic_alpha
    delta_ll_c_vs_b = best_grid["ll_c"] - fit_ab.ll_alpha

    return {
        # Grid result (locked gate reference)
        "best_beta_grid": best_grid["beta"],
        "best_alpha_c_grid": best_grid["alpha_c"],
        "chi2_c_grid": best_grid["chi2_c"],
        "ll_c_grid": best_grid["ll_c"],
        "bic_c_grid": best_grid["bic_c"],
        # Continuous cross-check (ternary search)
        "best_beta_continuous": beta_continuous,
        "best_alpha_c_continuous": alpha_cont,
        "chi2_c_continuous": chi2_cont,
        "ll_c_continuous": ll_cont,
        "bic_c_continuous": bic_cont,
        "beta_grid_vs_continuous_diff": abs(best_grid["beta"] - beta_continuous),
        # Comparisons vs A and B
        "delta_bic_c_vs_a": delta_bic_c_vs_a,
        "delta_bic_c_vs_b": delta_bic_c_vs_b,
        "delta_ll_c_vs_b": delta_ll_c_vs_b,
        "model_c_preferred_over_b": delta_bic_c_vs_b < -2.0,
        # BIC penalty
        "bic_penalty_k2_vs_k1": math.log(n),  # extra penalty for k=2 vs k=1
        "grid": grid_rows,
    }


def bootstrap_beta(df: pd.DataFrame, n_runs: int = 500, seed: int = 20260228) -> List[float]:
    rng = random.Random(seed)
    n = len(df)
    betas = []
    for _ in range(n_runs):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        sample = df.iloc[idx].reset_index(drop=True)
        best_chi2 = None
        best_beta = None
        for beta in BETA_GRID:
            _, chi2_c, _ = _fit_power_law_beta(sample, beta)
            if best_chi2 is None or chi2_c < best_chi2:
                best_chi2 = chi2_c
                best_beta = beta
        if best_beta is not None:
            betas.append(best_beta)
    return betas


# ---------------------------------------------------------------------------
# Shuffle control
# ---------------------------------------------------------------------------

def shuffle_control(df: pd.DataFrame, runs: int = 400, seed: int = 20260227) -> dict:
    rng = random.Random(seed)
    mass_list = list(df["spacecraft_mass_kg"])
    deltas = []
    for _ in range(runs):
        shuffled = df.copy()
        shuffled["spacecraft_mass_kg"] = rng.sample(mass_list, len(mass_list))
        fit = fit_models(shuffled)
        deltas.append(fit.delta_bic)
    s = pd.Series(deltas)
    return {
        "delta_bic_median": float(s.median()),
        "delta_bic_mean": float(s.mean()),
        "delta_bic_p10": float(s.quantile(0.10)),
        "delta_bic_p90": float(s.quantile(0.90)),
    }


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--derived",
        default=str(
            ROOT / "05_validation" / "evidence" / "artifacts"
            / "qng-t-028-post-horizons-2026-02-21" / "flyby-derived.csv"
        ),
    )
    parser.add_argument(
        "--base",
        default=str(ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"),
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-straton-002"),
    )
    parser.add_argument("--bootstrap-runs", type=int, default=400)
    parser.add_argument("--shuffle-runs", type=int, default=400)
    parser.add_argument("--modelc-bootstrap-runs", type=int, default=500)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Load and filter ---
    df = load_data(Path(args.derived), Path(args.base))
    n_classic = len(df)
    n_missions = df["mission_id"].nunique() if "mission_id" in df.columns else "unknown"
    print(f"[dataset] n={n_classic} rows, {n_missions} missions")

    # --- Model A + B fit (with full BIC decomposition) ---
    fit = fit_models(df)
    print(f"[fit] delta_bic={fit.delta_bic:.4f}  delta_ll={fit.delta_ll:.4f}")
    print(f"[fit] alpha={fit.alpha:.4e}  tau_const={fit.tau_const:.4e}")
    print(f"[sigma] min={fit.sigma_min:.4e}  median={fit.sigma_median:.4e}  max={fit.sigma_max:.4e}")

    # --- Bootstrap alpha (gate 2) ---
    alpha_samples = bootstrap_alpha(df, n_runs=args.bootstrap_runs, seed=20260225)
    alpha_series = pd.Series(alpha_samples)
    mean_alpha = alpha_series.mean()
    alpha_cv = float(abs(alpha_series.std(ddof=1) / mean_alpha)) if mean_alpha != 0 else float("inf")
    print(f"[bootstrap] alpha CV={alpha_cv:.3f}")

    # --- Residuals diagnostic (D4) ---
    resid_records = residuals_diagnostic(df, fit)
    n_leverage = sum(1 for r in resid_records if r["leverage_flag"])
    print(f"[residuals] {n_leverage} rows with |std_residual_B| > 2.0 (leverage)")

    # --- Exact LOO (gate 4 + D1) ---
    loo_row_records = loo_rows(df)
    loo_pass_count = sum(1 for r in loo_row_records if r["gate_pass"])
    loo_fraction = loo_pass_count / len(loo_row_records) if loo_row_records else 0.0
    print(f"[loo-rows] {loo_pass_count}/{len(loo_row_records)} pass  fraction={loo_fraction:.3f}")

    # --- Mission LOO (D2) ---
    loo_mission_records = loo_missions(df)
    miss_pass = sum(1 for r in loo_mission_records if r["gate_pass"])
    print(f"[loo-missions] {miss_pass}/{len(loo_mission_records)} mission groups pass")

    # --- Shuffle control (gate 3) ---
    shuffle_stats = shuffle_control(df, runs=args.shuffle_runs, seed=20260227)
    print(f"[shuffle] median delta_bic={shuffle_stats['delta_bic_median']:.3f}")

    # --- Model C power law (D3) ---
    modelc = fit_power_law(df, fit)
    beta_samples = bootstrap_beta(df, n_runs=args.modelc_bootstrap_runs, seed=20260228)
    beta_series = pd.Series(beta_samples)
    beta_ci_lo = float(beta_series.quantile(0.025))
    beta_ci_hi = float(beta_series.quantile(0.975))
    if modelc:
        print(f"[model-c] beta_grid={modelc['best_beta_grid']}  "
              f"beta_continuous={modelc['best_beta_continuous']:.4f}  "
              f"CI=[{beta_ci_lo:.2f},{beta_ci_hi:.2f}]  "
              f"delta_bic(C-B)={modelc['delta_bic_c_vs_b']:.3f}")

    # --- Gates ---
    gate_bic = fit.delta_bic <= -10.0
    gate_alpha_cv = alpha_cv < 0.30
    gate_shuffle = shuffle_stats["delta_bic_median"] > -2.0
    gate_leaveout = loo_fraction >= 0.90
    decision = gate_bic and gate_alpha_cv and gate_shuffle and gate_leaveout

    print(f"\n[gates]")
    print(f"  G1 delta_bic <= -10:    {'PASS' if gate_bic else 'FAIL'}  ({fit.delta_bic:.4f})")
    print(f"  G2 alpha CV < 0.30:     {'PASS' if gate_alpha_cv else 'FAIL'}  ({alpha_cv:.3f})")
    print(f"  G3 shuffle median > -2: {'PASS' if gate_shuffle else 'FAIL'}  ({shuffle_stats['delta_bic_median']:.3f})")
    print(f"  G4 LOO frac >= 0.90:    {'PASS' if gate_leaveout else 'FAIL'}  ({loo_fraction:.3f}, {loo_pass_count}/{len(loo_row_records)})")
    print(f"  DECISION: {'PASS' if decision else 'FAIL'}")

    # --- Write outputs ---

    # fit-summary.csv: gates + core metrics
    write_csv(out_dir / "fit-summary.csv", [
        {"metric": "n_classic_rows", "value": n_classic},
        {"metric": "n_missions", "value": n_missions},
        {"metric": "sigma_min", "value": fit.sigma_min},
        {"metric": "sigma_median", "value": fit.sigma_median},
        {"metric": "sigma_max", "value": fit.sigma_max},
        {"metric": "tau_const", "value": fit.tau_const},
        {"metric": "alpha", "value": fit.alpha},
        {"metric": "delta_bic", "value": fit.delta_bic},
        {"metric": "delta_ll", "value": fit.delta_ll},
        {"metric": "alpha_cv_bootstrap", "value": alpha_cv},
        {"metric": "loo_pass_fraction", "value": loo_fraction},
        {"metric": "loo_pass_count", "value": loo_pass_count},
        {"metric": "loo_total_rows", "value": len(loo_row_records)},
        {"metric": "shuffle_delta_bic_median", "value": shuffle_stats["delta_bic_median"]},
        {"metric": "shuffle_delta_bic_mean", "value": shuffle_stats["delta_bic_mean"]},
        {"metric": "shuffle_delta_bic_p10", "value": shuffle_stats["delta_bic_p10"]},
        {"metric": "shuffle_delta_bic_p90", "value": shuffle_stats["delta_bic_p90"]},
        {"metric": "gate_pass_delta_bic", "value": gate_bic},
        {"metric": "gate_pass_alpha_cv", "value": gate_alpha_cv},
        {"metric": "gate_pass_shuffle", "value": gate_shuffle},
        {"metric": "gate_pass_leaveout", "value": gate_leaveout},
        {"metric": "decision", "value": decision},
    ])

    # bic-decomposition.csv: full transparency
    write_csv(out_dir / "bic-decomposition.csv", [
        {"model": "A_null",    "k": 1, "n": n_classic,
         "ll": fit.ll_const,  "bic": fit.bic_const,  "chi2": fit.chi2_const,
         "param": fit.tau_const,  "param_name": "tau_const"},
        {"model": "B_straton", "k": 1, "n": n_classic,
         "ll": fit.ll_alpha,  "bic": fit.bic_alpha,  "chi2": fit.chi2_alpha,
         "param": fit.alpha,      "param_name": "alpha"},
        {"model": "delta_B_minus_A", "k": "-", "n": n_classic,
         "ll": fit.delta_ll,  "bic": fit.delta_bic,  "chi2": fit.chi2_alpha - fit.chi2_const,
         "param": None, "param_name": "delta"},
    ])

    write_csv(out_dir / "residuals-diagnostic.csv", resid_records)
    write_csv(out_dir / "loo-row-influence.csv", loo_row_records)
    write_csv(out_dir / "loo-mission-influence.csv", loo_mission_records)
    write_csv(out_dir / "bootstrap-alpha.csv", [{"alpha": v} for v in alpha_samples])
    write_csv(out_dir / "bootstrap-beta-modelc.csv", [{"beta": v} for v in beta_samples])
    write_csv(out_dir / "negative-controls-summary.csv", [shuffle_stats])

    if modelc:
        write_csv(out_dir / "model-c-grid.csv", modelc.get("grid", []))
        write_csv(out_dir / "model-c-report.csv", [{
            "best_beta_grid": modelc["best_beta_grid"],
            "best_alpha_c_grid": modelc["best_alpha_c_grid"],
            "ll_c_grid": modelc["ll_c_grid"],
            "bic_c_grid": modelc["bic_c_grid"],
            "best_beta_continuous": modelc["best_beta_continuous"],
            "best_alpha_c_continuous": modelc["best_alpha_c_continuous"],
            "ll_c_continuous": modelc["ll_c_continuous"],
            "bic_c_continuous": modelc["bic_c_continuous"],
            "beta_grid_vs_continuous_diff": modelc["beta_grid_vs_continuous_diff"],
            "delta_bic_c_vs_a": modelc["delta_bic_c_vs_a"],
            "delta_bic_c_vs_b": modelc["delta_bic_c_vs_b"],
            "delta_ll_c_vs_b": modelc["delta_ll_c_vs_b"],
            "model_c_preferred_over_b": modelc["model_c_preferred_over_b"],
            "bic_penalty_k2_vs_k1": modelc["bic_penalty_k2_vs_k1"],
            "beta_ci_lo_95": beta_ci_lo,
            "beta_ci_hi_95": beta_ci_hi,
        }])

    write_text(out_dir / "run-log.txt", json.dumps({
        "script": "run_qng_t_straton_002.py",
        "authored_by": "Claude Sonnet 4.6 (2026-02-22)",
        "derived_path": rel_path(Path(args.derived)),
        "base_path": rel_path(Path(args.base)),
        "n_classic_rows": n_classic,
        "classic_pass_ids": sorted(CLASSIC_PASS_IDS),
        "bootstrap_runs": args.bootstrap_runs,
        "shuffle_runs": args.shuffle_runs,
        "modelc_bootstrap_runs": args.modelc_bootstrap_runs,
        "seeds": {
            "bootstrap_alpha": 20260225,
            "shuffle": 20260227,
            "modelc_bootstrap": 20260228,
        },
    }, indent=2))

    # --- Markdown report ---
    bic_penalty = math.log(n_classic)
    lines = [
        "# QNG-T-STRATON-002 Report",
        "Authored by: Claude Sonnet 4.6",
        "",
        f"- Dataset: DS-005 classic subset — n={n_classic} rows, {n_missions} missions",
        f"- Excluded: JUNO_1, BEPICOLOMBO_1, SOLAR_ORBITER_1 (placeholder residuals)",
        "",
        "## BIC Decomposition",
        "",
        "| Model | k | n | LL | BIC | chi2 | param |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        f"| A (null)    | 1 | {n_classic} | {fit.ll_const:.4f} | {fit.bic_const:.4f} | {fit.chi2_const:.4f} | tau_const={fit.tau_const:.4e} |",
        f"| B (straton) | 1 | {n_classic} | {fit.ll_alpha:.4f} | {fit.bic_alpha:.4f} | {fit.chi2_alpha:.4f} | alpha={fit.alpha:.4e} |",
        f"| delta (B-A) | - | - | {fit.delta_ll:.4f} | {fit.delta_bic:.4f} | {fit.chi2_alpha - fit.chi2_const:.4f} | - |",
        "",
        "## Sigma Summary",
        "",
        f"| min | median | max |",
        f"| --- | --- | --- |",
        f"| {fit.sigma_min:.4e} | {fit.sigma_median:.4e} | {fit.sigma_max:.4e} |",
        "",
        "## Gates",
        "",
        f"| Gate | Threshold | Value | Status |",
        f"| --- | --- | --- | --- |",
        f"| G1 delta_bic | <= -10 | {fit.delta_bic:.4f} | {'PASS' if gate_bic else 'FAIL'} |",
        f"| G2 alpha CV | < 0.30 | {alpha_cv:.3f} | {'PASS' if gate_alpha_cv else 'FAIL'} |",
        f"| G3 shuffle median | > -2.0 | {shuffle_stats['delta_bic_median']:.3f} | {'PASS' if gate_shuffle else 'FAIL'} |",
        f"| G4 LOO fraction | >= 0.90 | {loo_fraction:.3f} ({loo_pass_count}/{len(loo_row_records)}) | {'PASS' if gate_leaveout else 'FAIL'} |",
        "",
        f"**Decision: {'PASS' if decision else 'FAIL'}**",
        "",
        "## Residuals Diagnostic (D4)",
        "",
        "| pass_id | mass_kg | sigma | std_resid_A | std_resid_B | leverage |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in resid_records:
        lines.append(
            f"| {r['pass_id']} | {r['mass_kg']:.0f} | {r['sigma']:.4e} | "
            f"{r['std_residual_A']:.3f} | {r['std_residual_B']:.3f} | "
            f"{'YES' if r['leverage_flag'] else 'no'} |"
        )

    lines += [
        "",
        "## LOO Row Influence (D1)",
        "",
        "| pass_id | mission | mass_kg | delta_alpha_rel_pct | delta_bic_loo | gate |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in loo_row_records:
        lines.append(
            f"| {r['pass_id']} | {r['mission_id']} | {r['mass_kg']:.0f} | "
            f"{r['delta_alpha_rel_pct']:.1f}% | {r['delta_bic_loo']:.2f} | "
            f"{'OK' if r['gate_pass'] else 'LEVERAGE'} |"
        )

    lines += [
        "",
        "## LOO Mission Influence (D2)",
        "",
        "| mission_id | n_rows | delta_alpha_rel_pct | delta_bic_loo | gate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in loo_mission_records:
        lines.append(
            f"| {r['mission_id']} | {r['n_rows_dropped']} | "
            f"{r['delta_alpha_rel_pct']:.1f}% | {r['delta_bic_loo']:.2f} | "
            f"{'OK' if r['gate_pass'] else 'LEVERAGE'} |"
        )

    if modelc:
        lines += [
            "",
            "## Model C: Power Law (diagnostic only)",
            "",
            f"BIC penalty for k=2 vs k=1: ln({n_classic}) = {bic_penalty:.4f}",
            "",
            "| | Grid (locked) | Continuous (cross-check) |",
            "| --- | --- | --- |",
            f"| best beta | {modelc['best_beta_grid']} | {modelc['best_beta_continuous']:.4f} |",
            f"| best alpha_c | {modelc['best_alpha_c_grid']:.4e} | {modelc['best_alpha_c_continuous']:.4e} |",
            f"| LL | {modelc['ll_c_grid']:.4f} | {modelc['ll_c_continuous']:.4f} |",
            f"| BIC (k=2) | {modelc['bic_c_grid']:.4f} | {modelc['bic_c_continuous']:.4f} |",
            f"| grid vs continuous diff | {modelc['beta_grid_vs_continuous_diff']:.4f} | - |",
            "",
            f"- delta_bic(C-A): {modelc['delta_bic_c_vs_a']:.4f}",
            f"- delta_bic(C-B): {modelc['delta_bic_c_vs_b']:.4f}  "
            f"({'C preferred over B' if modelc['model_c_preferred_over_b'] else 'B preferred or equal'})",
            f"- delta_ll(C-B): {modelc['delta_ll_c_vs_b']:.4f}",
            f"- beta 95% CI (bootstrap n={args.modelc_bootstrap_runs}): [{beta_ci_lo:.2f}, {beta_ci_hi:.2f}]",
        ]

    write_text(out_dir / "straton-002-report.md", "\n".join(lines))

    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
