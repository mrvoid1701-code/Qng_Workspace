"""
QNG-T-064: Acoustic scale ratio ell_D_P / ell_D_T from spectral dimension d_s.

Formula: ell_D_P / ell_D_T = d_s / (d_s - 2)

Inputs:
  --d-s       spectral dimension (default 4.082)
  --d-s-err   uncertainty on d_s (default 0.125)
  --ell-dt    observed ell_D_T from T-052 best-fit (default 576.144)
  --ell-dp    observed ell_D_P from T-052 best-fit (default 1134.984)
  --out-dir   output directory

Outputs:
  ratio-comparison.csv
  summary.md
  run-log.txt
"""

import argparse
import csv
import math
import os
import sys
import datetime


def predict_ratio(d_s):
    return d_s / (d_s - 2.0)


def predict_ratio_err(d_s, d_s_err):
    # d/d(d_s) [d_s / (d_s-2)] = -2 / (d_s-2)^2
    deriv = -2.0 / (d_s - 2.0) ** 2
    return abs(deriv) * d_s_err


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--d-s", type=float, default=4.082)
    parser.add_argument("--d-s-err", type=float, default=0.125)
    parser.add_argument("--ell-dt", type=float, default=576.144)
    parser.add_argument("--ell-dp", type=float, default=1134.984)
    parser.add_argument("--out-dir", type=str, default="05_validation/evidence/artifacts/qng-t-064")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    log_path = os.path.join(args.out_dir, "run-log.txt")
    log = open(log_path, "w")

    def emit(msg):
        print(msg)
        log.write(msg + "\n")

    emit(f"QNG-T-064  started  {datetime.datetime.utcnow().isoformat()}Z")
    emit(f"d_s          = {args.d_s} +/- {args.d_s_err}")
    emit(f"ell_D_T obs  = {args.ell_dt}")
    emit(f"ell_D_P obs  = {args.ell_dp}")
    emit("")

    # --- Observed ratio ---
    ratio_obs = args.ell_dp / args.ell_dt
    # Assume fitting uncertainty ~1% on each ell_D (conservative)
    ratio_obs_err = ratio_obs * math.sqrt(2) * 0.01

    emit(f"Observed ratio  = {ratio_obs:.6f}  (fitting err ~ {ratio_obs_err:.4f})")

    # --- Predicted ratio from formula ---
    ratio_pred = predict_ratio(args.d_s)
    ratio_pred_err = predict_ratio_err(args.d_s, args.d_s_err)

    emit(f"Predicted ratio = {ratio_pred:.6f}  (propagated err = {ratio_pred_err:.4f})")

    # --- Discrepancy ---
    delta = ratio_obs - ratio_pred
    # Combined sigma: quadrature of prediction error and observation error
    sigma_combined = math.sqrt(ratio_pred_err**2 + ratio_obs_err**2)
    n_sigma = abs(delta) / sigma_combined
    frac_err = abs(delta) / ratio_obs * 100.0

    emit("")
    emit(f"Delta           = {delta:+.6f}")
    emit(f"sigma_combined  = {sigma_combined:.4f}")
    emit(f"Discrepancy     = {n_sigma:.3f} sigma")
    emit(f"Fractional err  = {frac_err:.3f}%")

    # --- Pass/fail ---
    passed = n_sigma <= 2.0
    result = "PASS" if passed else "FAIL"
    emit("")
    emit(f"RESULT: {result}  (threshold: <= 2 sigma, achieved {n_sigma:.3f} sigma)")

    # --- Sensitivity sweep: ratio over d_s range ---
    emit("")
    emit("Sensitivity table (d_s range):")
    emit(f"{'d_s':>8}  {'ratio_pred':>12}  {'delta_sigma':>12}")
    sweep_rows = []
    for ds_val in [args.d_s - args.d_s_err, args.d_s, args.d_s + args.d_s_err]:
        rp = predict_ratio(ds_val)
        d = ratio_obs - rp
        ns = abs(d) / sigma_combined
        emit(f"{ds_val:8.3f}  {rp:12.6f}  {ns:12.3f}")
        sweep_rows.append({"d_s": ds_val, "ratio_pred": rp, "ratio_obs": ratio_obs,
                            "delta": d, "n_sigma": ns})

    log.close()

    # --- CSV ---
    csv_path = os.path.join(args.out_dir, "ratio-comparison.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quantity", "value", "uncertainty"])
        w.writeheader()
        w.writerow({"quantity": "d_s", "value": args.d_s, "uncertainty": args.d_s_err})
        w.writerow({"quantity": "ratio_observed", "value": ratio_obs, "uncertainty": ratio_obs_err})
        w.writerow({"quantity": "ratio_predicted", "value": ratio_pred, "uncertainty": ratio_pred_err})
        w.writerow({"quantity": "delta", "value": delta, "uncertainty": sigma_combined})
        w.writerow({"quantity": "n_sigma", "value": n_sigma, "uncertainty": 0})
        w.writerow({"quantity": "frac_err_pct", "value": frac_err, "uncertainty": 0})

    # --- summary.md ---
    status_icon = "PASS" if passed else "FAIL"
    md = f"""# QNG-T-064 Summary

**Claim:** QNG-C-119 — ell_D_P / ell_D_T = d_s / (d_s - 2)
**Result:** {status_icon}
**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d')}

## Values

| Quantity | Value | Uncertainty |
|----------|-------|-------------|
| d_s | {args.d_s} | ± {args.d_s_err} |
| ell_D_T (observed, T-052) | {args.ell_dt} | ~1% fitting |
| ell_D_P (observed, T-052) | {args.ell_dp} | ~1% fitting |
| Ratio observed | {ratio_obs:.6f} | ± {ratio_obs_err:.4f} |
| Ratio predicted | {ratio_pred:.6f} | ± {ratio_pred_err:.4f} |
| Delta | {delta:+.6f} | — |
| Discrepancy | {n_sigma:.3f} σ | — |
| Fractional error | {frac_err:.3f}% | — |

## Interpretation

Formula: **ell_D_P / ell_D_T = d_s / (d_s − 2)**

With d_s = {args.d_s} ± {args.d_s_err}:
- Predicted ratio = {ratio_pred:.4f} ± {ratio_pred_err:.4f}
- Observed ratio  = {ratio_obs:.4f} ± {ratio_obs_err:.4f}
- Discrepancy = **{n_sigma:.3f} sigma** (threshold: 2 sigma)

This is a **parameter-free** prediction: d_s is measured independently from the Jaccard
graph (G18d v2) and ell_D_T, ell_D_P from the T-052 CMB best-fit. No fitting was performed here.

## Pass Criterion

- Threshold: discrepancy ≤ 2 sigma
- Achieved: {n_sigma:.3f} sigma
- **{status_icon}**
"""
    with open(os.path.join(args.out_dir, "summary.md"), "w") as f:
        f.write(md)

    print(f"\nOutputs written to {args.out_dir}/")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
