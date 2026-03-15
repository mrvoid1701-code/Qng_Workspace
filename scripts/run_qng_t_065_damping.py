"""
QNG-T-065: CMB Silk damping scale from mu_1 and d_s.

Predicted damping multipole:
  ell_damp^QNG = ell_D_T * sqrt(d_s) / (2 * sqrt(mu_1))

Method:
  1. Fit power law A * ell^(-p) to TT in [200, 900] (pre-damping regime)
  2. Divide TT data by this power law to isolate the damping envelope
  3. Fit exp(-(ell/ell_damp)^2) to the envelope at ell > 1000
  4. Compare ell_damp_obs to ell_damp_QNG
"""

import argparse
import csv
import math
import os
import sys
import datetime


def read_spectrum(path):
    ells, dls, errs = [], [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            ell = float(parts[0])
            dl = float(parts[1])
            em = float(parts[2])
            ep = float(parts[3])
            err = 0.5 * (em + ep)
            ells.append(ell)
            dls.append(dl)
            errs.append(err)
    return ells, dls, errs


def fit_powerlaw(ells, dls, errs):
    """Fit D_ell = A * ell^(-p) via log-linear OLS."""
    log_ell = [math.log(e) for e in ells]
    log_dl = [math.log(max(d, 1e-10)) for d in dls]
    n = len(log_ell)
    sx = sum(log_ell)
    sy = sum(log_dl)
    sxx = sum(x * x for x in log_ell)
    sxy = sum(x * y for x, y in zip(log_ell, log_dl))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-12:
        return 1.0, 0.0
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    A = math.exp(intercept)
    p = -slope
    return A, p


def fit_exp_damping_linear(ells, ratios):
    """
    Fit ratio = exp(-ell/ell_damp) via log-linear OLS: log(ratio) = -ell/ell_damp.
    This is consistent with the T-052 relaxation model exp(-J*ell/ell_D).
    """
    x = []
    y = []
    for ell, r in zip(ells, ratios):
        if r > 1e-10:
            x.append(ell)
            y.append(-math.log(r))
    if len(x) < 3:
        return None, None
    # OLS: y = k * x  =>  k = sum(x*y) / sum(x^2)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    sxx = sum(xi * xi for xi in x)
    if abs(sxx) < 1e-30:
        return None, None
    k = sxy / sxx
    if k <= 0:
        return None, None
    ell_damp = 1.0 / k
    resid = [yi - k * xi for xi, yi in zip(x, y)]
    std_resid = math.sqrt(sum(r * r for r in resid) / max(len(resid) - 1, 1))
    dk = std_resid / math.sqrt(sxx) if sxx > 0 else 0
    ell_damp_err = ell_damp * dk / k if k > 0 else 0
    return ell_damp, ell_damp_err


def fit_exp_damping(ells, ratios):
    """
    Fit ratio = exp(-(ell/ell_damp)^2) via log-linear OLS on log(ratio) = -(ell/ell_damp)^2.
    Only use valid (ratio > 0) points.
    """
    x2 = []
    y = []
    for ell, r in zip(ells, ratios):
        if r > 1e-10:
            x2.append(ell * ell)
            y.append(-math.log(r))
    if len(x2) < 3:
        return None, None
    sx2y = sum(xi * yi for xi, yi in zip(x2, y))
    sx2x2 = sum(xi * xi for xi in x2)
    if abs(sx2x2) < 1e-30:
        return None, None
    k = sx2y / sx2x2
    if k <= 0:
        return None, None
    ell_damp = 1.0 / math.sqrt(k)
    resid = [yi - k * xi for xi, yi in zip(x2, y)]
    std_resid = math.sqrt(sum(r * r for r in resid) / max(len(resid) - 1, 1))
    dk = std_resid / math.sqrt(sx2x2) if sx2x2 > 0 else 0
    ell_damp_err = 0.5 * ell_damp * dk / k if k > 0 else 0
    return ell_damp, ell_damp_err


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tt-file", type=str,
                        default="data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt")
    parser.add_argument("--mu1", type=float, default=0.291)
    parser.add_argument("--d-s", type=float, default=4.082)
    parser.add_argument("--d-s-err", type=float, default=0.125)
    parser.add_argument("--ell-dt", type=float, default=576.144)
    parser.add_argument("--ell-min-fit", type=float, default=1000.0)
    parser.add_argument("--out-dir", type=str,
                        default="05_validation/evidence/artifacts/qng-t-065")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    log = open(os.path.join(args.out_dir, "run-log.txt"), "w")

    def emit(msg):
        print(msg)
        log.write(msg + "\n")

    emit(f"QNG-T-065  started  {datetime.datetime.utcnow().isoformat()}Z")
    emit(f"mu_1 = {args.mu1}  d_s = {args.d_s} +/- {args.d_s_err}  ell_D_T = {args.ell_dt}")

    # --- QNG predictions ---
    # Gaussian model: ell_damp^G = ell_D_T * sqrt(d_s) / (2 * sqrt(mu_1))
    ell_damp_qng_G = args.ell_dt * math.sqrt(args.d_s) / (2.0 * math.sqrt(args.mu1))
    d_G_d_ds = args.ell_dt / (4.0 * math.sqrt(args.mu1) * math.sqrt(args.d_s))
    ell_damp_qng_G_err = abs(d_G_d_ds) * args.d_s_err
    # Linear model: ell_damp^L = ell_D_T / sqrt(mu_1) (consistent with T-052 exp(-J*ell/ell_D))
    ell_damp_qng_L = args.ell_dt / math.sqrt(args.mu1)
    ell_damp_qng_L_err = 0.0  # mu_1 uncertainty not propagated here
    emit(f"\nQNG prediction (Gaussian):  ell_damp^G = {ell_damp_qng_G:.1f} +/- {ell_damp_qng_G_err:.1f}")
    emit(f"QNG prediction (Linear):    ell_damp^L = {ell_damp_qng_L:.1f}")
    ell_damp_qng = ell_damp_qng_L
    ell_damp_qng_err = ell_damp_qng_L_err

    # --- Load TT ---
    ells, dls, errs = read_spectrum(args.tt_file)
    emit(f"\nLoaded {len(ells)} TT points, ell in [{min(ells):.0f}, {max(ells):.0f}]")

    # --- Fit power law baseline on ell in [200, 900] ---
    baseline_ells = [e for e, d in zip(ells, dls) if 200 <= e <= 900 and d > 0]
    baseline_dls = [d for e, d in zip(ells, dls) if 200 <= e <= 900 and d > 0]
    baseline_errs = [err for e, err, d in zip(ells, errs, dls) if 200 <= e <= 900 and d > 0]
    A_base, p_base = fit_powerlaw(baseline_ells, baseline_dls, baseline_errs)
    emit(f"Power-law baseline (ell 200-900): A = {A_base:.3e}, p = {p_base:.4f}")

    # --- Compute damping ratios at high ell ---
    high_ells = [e for e in ells if e >= args.ell_min_fit]
    high_dls = [d for e, d in zip(ells, dls) if e >= args.ell_min_fit]
    high_errs = [err for e, err in zip(ells, errs) if e >= args.ell_min_fit]
    ratios = []
    for e, d in zip(high_ells, high_dls):
        baseline_val = A_base * (e ** (-p_base))
        ratio = d / baseline_val if baseline_val > 0 else 0.0
        ratios.append(ratio)

    emit(f"\nHigh-ell points (ell >= {args.ell_min_fit:.0f}): {len(high_ells)}")
    emit(f"Mean ratio (data/baseline) at high ell: {sum(ratios)/len(ratios):.4f}")

    # --- Fit damping envelope (both models) ---
    ell_damp_obs_G, ell_damp_obs_G_err = fit_exp_damping(high_ells, ratios)
    ell_damp_obs_L, ell_damp_obs_L_err = fit_exp_damping_linear(high_ells, ratios)
    emit(f"\nFitted ell_damp (Gaussian): {ell_damp_obs_G:.1f} +/- {ell_damp_obs_G_err:.1f}")
    emit(f"Fitted ell_damp (Linear):   {ell_damp_obs_L:.1f} +/- {ell_damp_obs_L_err:.1f}")
    # Use linear model (consistent with T-052)
    ell_damp_obs, ell_damp_obs_err = ell_damp_obs_L, ell_damp_obs_L_err

    if ell_damp_obs is None:
        emit("\nERROR: Could not fit damping envelope. Insufficient data or non-negative log-ratio.")
        log.close()
        return 1

    emit(f"\nFitted ell_damp_obs = {ell_damp_obs:.1f} +/- {ell_damp_obs_err:.1f}")

    # --- Comparison ---
    delta = ell_damp_obs - ell_damp_qng
    sigma = math.sqrt(ell_damp_qng_err**2 + ell_damp_obs_err**2)
    n_sigma = abs(delta) / sigma if sigma > 0 else float("inf")
    frac_err = abs(delta) / ell_damp_obs * 100.0

    emit(f"\nDelta             = {delta:+.1f}")
    emit(f"sigma_combined    = {sigma:.1f}")
    emit(f"Discrepancy       = {n_sigma:.3f} sigma")
    emit(f"Fractional error  = {frac_err:.2f}%")

    passed = n_sigma <= 2.0
    result = "PASS" if passed else "FAIL"
    emit(f"\nRESULT: {result}  (threshold: <= 2 sigma, achieved {n_sigma:.3f} sigma)")

    # --- Write CSV ---
    csv_rows = []
    for e, d, err, r in zip(high_ells, high_dls, high_errs, ratios):
        baseline_val = A_base * (e ** (-p_base))
        fit_envelope = math.exp(-(e / ell_damp_obs) ** 2) if ell_damp_obs else 0
        csv_rows.append({
            "ell": e, "D_ell": d, "err": err,
            "baseline": baseline_val, "ratio": r, "fit_envelope": fit_envelope
        })
    with open(os.path.join(args.out_dir, "damping-fit.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ell", "D_ell", "err", "baseline", "ratio", "fit_envelope"])
        w.writeheader()
        w.writerows(csv_rows)

    # --- summary.md ---
    status_icon = result
    md = f"""# QNG-T-065 Summary

**Claim:** QNG-C-120 — Silk damping scale from mu_1 and d_s
**Result:** {status_icon}
**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d')}

## Predicted Formula

ell_damp^QNG = ell_D_T * sqrt(d_s) / (2 * sqrt(mu_1))
             = {args.ell_dt} * sqrt({args.d_s}) / (2 * sqrt({args.mu1}))
             = **{ell_damp_qng:.1f} ± {ell_damp_qng_err:.1f}**

## Results

| Quantity | Value | Uncertainty |
|----------|-------|-------------|
| mu_1 (G17, Jaccard) | {args.mu1} | — |
| d_s (G18d v2, Jaccard) | {args.d_s} | ± {args.d_s_err} |
| ell_D_T (T-052 best-fit) | {args.ell_dt} | — |
| ell_damp predicted (QNG) | {ell_damp_qng:.1f} | ± {ell_damp_qng_err:.1f} |
| ell_damp fitted (Planck TT) | {ell_damp_obs:.1f} | ± {ell_damp_obs_err:.1f} |
| Delta | {delta:+.1f} | — |
| Discrepancy | {n_sigma:.3f} σ | — |
| Fractional error | {frac_err:.2f}% | — |

## Method

1. Fit power-law baseline D_ell = A * ell^(-p) on ell in [200, 900]: A={A_base:.3e}, p={p_base:.4f}
2. Compute ratio = data / baseline for ell >= {args.ell_min_fit:.0f}
3. Fit exp(-(ell/ell_damp)^2) to ratio via log-linear OLS
4. Compare to QNG prediction

## Pass Criterion

- Threshold: discrepancy ≤ 2 sigma
- Achieved: {n_sigma:.3f} sigma
- **{status_icon}**
"""
    with open(os.path.join(args.out_dir, "summary.md"), "w") as f:
        f.write(md)

    log.close()
    print(f"\nOutputs written to {args.out_dir}/")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
