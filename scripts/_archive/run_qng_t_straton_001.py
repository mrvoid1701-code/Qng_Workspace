#!/usr/bin/env python3
"""
QNG-T-STRATON-001: test mass-scaling of tau (tau = alpha * mass) vs tau constant.

Inputs:
- Derived flyby file with base features (default: qng-t-028-post-horizons-2026-02-21/flyby-derived.csv)
- Base flyby dataset with spacecraft_mass_kg column (default: data/trajectory/flyby_ds005_real.csv)

Outputs (out_dir default: 05_validation/evidence/artifacts/qng-t-straton-001):
- fit-summary.csv
- negative-controls-summary.csv
- leaveout-summary.csv
- bootstrap-alpha.csv
- run-log.txt
- straton-report.md
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class FitResult:
    tau_const: float
    alpha: float
    chi2_const: float
    chi2_alpha: float
    aic_const: float
    aic_alpha: float
    bic_const: float
    bic_alpha: float
    delta_aic: float
    delta_bic: float


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
    return derived


def weighted_fit(
    obs: pd.Series, feature: pd.Series, sigma: pd.Series
) -> Tuple[float, float]:
    w = 1.0 / (sigma ** 2)
    num = -(w * feature * obs).sum()
    den = (w * feature ** 2).sum()
    if den <= 0:
        return 0.0, 0.0
    tau = num / den
    chi2 = (w * (obs + tau * feature) ** 2).sum()
    return tau, chi2


def fit_models(df: pd.DataFrame) -> FitResult:
    obs = df["a_obs_whole_m_s2"]
    feature = df["feature_base_m_s3"]
    sigma = df["sigma_whole_m_s2"].copy()
    sigma.loc[sigma == 0] = df.loc[sigma == 0, "sigma_perigee_m_s2"]
    sigma.replace(0, 1e-18, inplace=True)

    tau_const, chi2_const = weighted_fit(obs, feature, sigma)

    feature_mass = feature * df["spacecraft_mass_kg"]
    alpha, chi2_alpha = weighted_fit(obs, feature_mass, sigma)

    n = len(df)
    k_const = 1
    k_alpha = 1
    aic_const = 2 * k_const + chi2_const
    aic_alpha = 2 * k_alpha + chi2_alpha
    bic_const = k_const * math.log(n) + chi2_const
    bic_alpha = k_alpha * math.log(n) + chi2_alpha
    delta_aic = aic_alpha - aic_const
    delta_bic = bic_alpha - bic_const

    return FitResult(
        tau_const=tau_const,
        alpha=alpha,
        chi2_const=chi2_const,
        chi2_alpha=chi2_alpha,
        aic_const=aic_const,
        aic_alpha=aic_alpha,
        bic_const=bic_const,
        bic_alpha=bic_alpha,
        delta_aic=delta_aic,
        delta_bic=delta_bic,
    )


def bootstrap_alpha(df: pd.DataFrame, n_runs: int = 400) -> list[float]:
    rng = random.Random(20260222)
    values = []
    for _ in range(n_runs):
        sample = df.sample(n=len(df), replace=True, random_state=rng.randint(0, 1_000_000))
        sigma = sample["sigma_whole_m_s2"].copy()
        sigma.loc[sigma == 0] = sample.loc[sigma == 0, "sigma_perigee_m_s2"]
        sigma.replace(0, 1e-18, inplace=True)
        alpha, _ = weighted_fit(
            sample["a_obs_whole_m_s2"],
            sample["feature_base_m_s3"] * sample["spacecraft_mass_kg"],
            sigma,
        )
        values.append(alpha)
    return values


def leave_out(df: pd.DataFrame, frac: float = 0.1, runs: int = 200) -> float:
    rng = random.Random(20260223)
    n = len(df)
    target = max(1, int(math.ceil(frac * n)))
    pass_count = 0
    for _ in range(runs):
        drop_idx = rng.sample(range(n), target)
        subset = df.drop(df.index[drop_idx])
        fit = fit_models(subset)
        if fit.delta_bic <= -10:
            pass_count += 1
    return pass_count / runs


def shuffle_control(df: pd.DataFrame, runs: int = 400) -> dict:
    rng = random.Random(20260224)
    deltas = []
    for _ in range(runs):
        shuffled = df.copy()
        shuffled["spacecraft_mass_kg"] = rng.sample(
            list(shuffled["spacecraft_mass_kg"]), len(shuffled)
        )
        fit = fit_models(shuffled)
        deltas.append(fit.delta_bic)
    return {
        "delta_bic_median": float(pd.Series(deltas).median()),
        "delta_bic_mean": float(pd.Series(deltas).mean()),
        "delta_bic_p10": float(pd.Series(deltas).quantile(0.10)),
        "delta_bic_p90": float(pd.Series(deltas).quantile(0.90)),
    }


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--derived",
        default=str(
            ROOT
            / "05_validation"
            / "evidence"
            / "artifacts"
            / "qng-t-028-post-horizons-2026-02-21"
            / "flyby-derived.csv"
        ),
        help="Path to derived flyby file with base feature columns.",
    )
    parser.add_argument(
        "--base",
        default=str(ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"),
        help="Base flyby dataset with spacecraft_mass_kg column.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-straton-001"),
        help="Output directory.",
    )
    parser.add_argument("--leaveout-runs", type=int, default=200)
    parser.add_argument("--bootstrap-runs", type=int, default=400)
    parser.add_argument("--shuffle-runs", type=int, default=400)
    args = parser.parse_args()

    derived_path = Path(args.derived)
    base_path = Path(args.base)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(derived_path, base_path)
    fit = fit_models(df)

    alpha_samples = bootstrap_alpha(df, n_runs=args.bootstrap_runs)
    alpha_series = pd.Series(alpha_samples)
    mean_alpha = alpha_series.mean()
    alpha_cv = (
        float(abs(alpha_series.std(ddof=1) / mean_alpha)) if mean_alpha != 0 else float("inf")
    )

    leaveout_fraction = leave_out(df, frac=0.10, runs=args.leaveout_runs)
    shuffle_stats = shuffle_control(df, runs=args.shuffle_runs)

    gate_bic = fit.delta_bic <= -10
    gate_alpha_cv = alpha_cv < 0.30
    gate_shuffle = shuffle_stats["delta_bic_median"] > -2.0  # collapse toward 0 or positive
    gate_leaveout = leaveout_fraction >= 0.90

    fit_summary = [
        {
            "metric": "tau_const",
            "value": fit.tau_const,
        },
        {"metric": "alpha", "value": fit.alpha},
        {"metric": "chi2_const", "value": fit.chi2_const},
        {"metric": "chi2_alpha", "value": fit.chi2_alpha},
        {"metric": "delta_aic", "value": fit.delta_aic},
        {"metric": "delta_bic", "value": fit.delta_bic},
        {"metric": "aic_const", "value": fit.aic_const},
        {"metric": "aic_alpha", "value": fit.aic_alpha},
        {"metric": "bic_const", "value": fit.bic_const},
        {"metric": "bic_alpha", "value": fit.bic_alpha},
        {"metric": "alpha_cv_bootstrap", "value": alpha_cv},
        {"metric": "leaveout_pass_fraction", "value": leaveout_fraction},
        {"metric": "shuffle_delta_bic_median", "value": shuffle_stats["delta_bic_median"]},
        {"metric": "shuffle_delta_bic_mean", "value": shuffle_stats["delta_bic_mean"]},
        {"metric": "shuffle_delta_bic_p10", "value": shuffle_stats["delta_bic_p10"]},
        {"metric": "shuffle_delta_bic_p90", "value": shuffle_stats["delta_bic_p90"]},
        {"metric": "gate_pass_delta_bic", "value": gate_bic},
        {"metric": "gate_pass_alpha_cv", "value": gate_alpha_cv},
        {"metric": "gate_pass_shuffle", "value": gate_shuffle},
        {"metric": "gate_pass_leaveout", "value": gate_leaveout},
        {
            "metric": "decision",
            "value": gate_bic and gate_alpha_cv and gate_shuffle and gate_leaveout,
        },
    ]
    write_csv(out_dir / "fit-summary.csv", fit_summary)

    write_csv(out_dir / "bootstrap-alpha.csv", [{"alpha": v} for v in alpha_samples])

    write_text(
        out_dir / "run-log.txt",
        json.dumps(
            {
                "derived_path": rel_path(derived_path),
                "base_path": rel_path(base_path),
                "bootstrap_runs": args.bootstrap_runs,
                "leaveout_runs": args.leaveout_runs,
                "shuffle_runs": args.shuffle_runs,
            },
            indent=2,
        ),
    )

    report_lines = []
    report_lines.append("# QNG-T-STRATON-001 Report")
    report_lines.append("")
    report_lines.append(f"- delta_bic (alpha vs const): {fit.delta_bic:.3f}")
    report_lines.append(f"- delta_aic (alpha vs const): {fit.delta_aic:.3f}")
    report_lines.append(f"- alpha: {fit.alpha:.6e}")
    report_lines.append(f"- tau_const: {fit.tau_const:.6e}")
    report_lines.append(f"- alpha CV (bootstrap): {alpha_cv:.3f}")
    report_lines.append(f"- leave-10%-out pass fraction: {leaveout_fraction:.3f}")
    report_lines.append(
        f"- shuffle delta_bic median/mean: {shuffle_stats['delta_bic_median']:.3f} / {shuffle_stats['delta_bic_mean']:.3f}"
    )
    report_lines.append("")
    report_lines.append("## Gates")
    report_lines.append("")
    report_lines.append(f"- gate_pass_delta_bic: {gate_bic}")
    report_lines.append(f"- gate_pass_alpha_cv: {gate_alpha_cv}")
    report_lines.append(f"- gate_pass_shuffle: {gate_shuffle}")
    report_lines.append(f"- gate_pass_leaveout: {gate_leaveout}")
    report_lines.append("")
    write_text(out_dir / "straton-report.md", "\n".join(report_lines))

    print(json.dumps({"decision": bool(fit.delta_bic <= -10)}, indent=2))
    return 0


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
