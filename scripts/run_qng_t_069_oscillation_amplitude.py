"""
QNG-T-069: Oscillation amplitude B from spectral dimension d_s.

Derivation (from QNG relaxation kernel):
  In the QNG stability field, acoustic oscillations decay exponentially over
  one acoustic period ell_A under the relaxation damping scale ell_D_T.
  The coherent fraction preserved is:

      B_TT = exp(-ell_A / ell_D_T) = exp(-2 / d_s)

  Because ell_A = 2 * ell_D_T / d_s  (from QNG-C-123 A4).

  For polarisation, ell_D_P replaces ell_D_T:
      B_EE = exp(-ell_A / ell_D_P)
      B_TE = sqrt(B_TT * B_EE)   (geometric mean, from QNG-C-123 A5)

Method:
  1. Fit TT spectrum (ell 30-2500) with A0, J, phi free; B on fine grid.
     ell_A, p_D_T, ell_D_T are theory-constrained (fixed).
  2. Compare B_TT_fitted to B_TT_pred = exp(-2/d_s).
  3. Pass: n_sigma <= 2.0

Pass criterion: n_sigma(B_TT) <= 2.0
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
            p = line.split()
            ells.append(float(p[0]))
            dls.append(float(p[1]))
            errs.append(0.5 * (float(p[2]) + float(p[3])))
    return ells, dls, errs


def chi2_model(ells, dls, errs, A0, p_D, ell_D, J, B, ell_A, phi):
    total = 0.0
    for e, d, err in zip(ells, dls, errs):
        if err <= 0:
            continue
        envelope = A0 * (e ** (-p_D)) * math.exp(-J * e / ell_D)
        pred = envelope * (1.0 + B * math.cos(2.0 * math.pi * e / ell_A + phi))
        total += ((d - pred) / err) ** 2
    return total


def fit_tt(ells, dls, errs, p_D, ell_D, ell_A, emit):
    fe = [e for e, d, err in zip(ells, dls, errs) if 30 <= e <= 2500 and err > 0 and d > 0]
    fd = [d for e, d, err in zip(ells, dls, errs) if 30 <= e <= 2500 and err > 0 and d > 0]
    ferr = [err for e, d, err in zip(ells, dls, errs) if 30 <= e <= 2500 and err > 0 and d > 0]
    n = len(fe)
    emit(f"  TT points in [30, 2500]: {n}")

    # Anchor A0 estimate at ell~550
    anchor = [(e, d) for e, d in zip(fe, fd) if 480 <= e <= 620]
    if anchor:
        ell_mid, dl_mid = anchor[len(anchor) // 2]
    else:
        ell_mid, dl_mid = fe[len(fe) // 2], fd[len(fd) // 2]
    A0_est = max(dl_mid * (ell_mid ** p_D), 1.0)

    # Step 1: coarse fit A0, J (B=0)
    best_A0, best_J, best_chi2 = A0_est, 0.0, float("inf")
    for A0f in [A0_est * f for f in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]]:
        for Jf in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]:
            c2 = chi2_model(fe, fd, ferr, A0f, p_D, ell_D, Jf, 0.0, ell_A, 0.0)
            if c2 < best_chi2:
                best_chi2 = c2
                best_A0 = A0f
                best_J = Jf

    # Step 2: fine grid A0, J
    for A0f in [best_A0 * f for f in [0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.15]]:
        for Jf in [max(0, best_J + dj) for dj in [-0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15]]:
            c2 = chi2_model(fe, fd, ferr, A0f, p_D, ell_D, Jf, 0.0, ell_A, 0.0)
            if c2 < best_chi2:
                best_chi2 = c2
                best_A0 = A0f
                best_J = Jf

    # Step 3: fine B grid + phi  [key part of this test]
    # Grid step = 0.025 so sigma_fit = 0.0125
    B_grid = [round(0.40 + i * 0.025, 3) for i in range(25)]  # 0.40 to 0.99
    phi_grid = [i * math.pi / 8 for i in range(16)]
    best_B, best_phi = 0.0, 0.0
    for Bf in B_grid:
        for phif in phi_grid:
            c2 = chi2_model(fe, fd, ferr, best_A0, p_D, ell_D, best_J, Bf, ell_A, phif)
            if c2 < best_chi2:
                best_chi2 = c2
                best_B = Bf
                best_phi = phif

    B_at_boundary = (best_B >= max(B_grid) - 0.001)
    emit(f"  Best fit: A0={best_A0:.3e}  J={best_J:.3f}  B={best_B:.4f}  phi={best_phi:.4f}")
    if B_at_boundary:
        emit("  *** WARNING: B at grid boundary ***")
    return best_A0, best_J, best_B, best_phi, n, B_at_boundary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tt-file", default="data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt")
    parser.add_argument("--d-s", type=float, default=4.082)
    parser.add_argument("--d-s-err", type=float, default=0.125)
    parser.add_argument("--ell-dt", type=float, default=576.144)
    parser.add_argument("--ell-dp", type=float, default=1134.984)
    parser.add_argument("--p-dt", type=float, default=1.119)
    parser.add_argument("--out-dir", default="05_validation/evidence/artifacts/qng-t-069")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    log = open(os.path.join(args.out_dir, "run-log.txt"), "w")

    def emit(msg):
        print(msg)
        log.write(msg + "\n")

    emit(f"QNG-T-069  started  {datetime.datetime.utcnow().isoformat()}Z")

    # --- Theory predictions ---
    d_s = args.d_s
    ell_D_T = args.ell_dt
    ell_D_P = args.ell_dp
    ell_A = 2.0 * ell_D_T / d_s

    B_TT_pred = math.exp(-ell_A / ell_D_T)   # = exp(-2/d_s)
    B_EE_pred = math.exp(-ell_A / ell_D_P)
    B_TE_pred = math.sqrt(B_TT_pred * B_EE_pred)

    # Uncertainty on B_TT from d_s uncertainty
    # dB/dd_s = B * 2/d_s^2
    dB_dds = B_TT_pred * 2.0 / d_s**2
    sigma_B_pred = abs(dB_dds) * args.d_s_err
    # Fitting uncertainty: half the B grid step = 0.025/2
    sigma_B_fit = 0.025 / 2.0
    sigma_B_total = math.sqrt(sigma_B_pred**2 + sigma_B_fit**2)

    emit(f"\nTheory parameters:")
    emit(f"  d_s      = {d_s} +/- {args.d_s_err}")
    emit(f"  ell_D_T  = {ell_D_T}")
    emit(f"  ell_D_P  = {ell_D_P}")
    emit(f"  ell_A    = 2*ell_D_T/d_s = {ell_A:.3f}")
    emit(f"\nQNG oscillation amplitude predictions:")
    emit(f"  B_TT = exp(-ell_A/ell_D_T) = exp(-2/d_s) = exp(-{2/d_s:.4f}) = {B_TT_pred:.6f}")
    emit(f"  B_EE = exp(-ell_A/ell_D_P) = exp(-{ell_A/ell_D_P:.4f}) = {B_EE_pred:.6f}")
    emit(f"  B_TE = sqrt(B_TT*B_EE) = {B_TE_pred:.6f}")
    emit(f"  sigma_B_pred (from d_s err) = {sigma_B_pred:.5f}")
    emit(f"  sigma_B_fit  (grid step/2)  = {sigma_B_fit:.5f}")
    emit(f"  sigma_B_total               = {sigma_B_total:.5f}")

    # --- Fit TT ---
    ells, dls, errs = read_spectrum(args.tt_file)
    emit(f"\nFitting TT spectrum:")
    A0, J, B_fit, phi_fit, n_pts, at_boundary = fit_tt(
        ells, dls, errs, args.p_dt, ell_D_T, ell_A, emit
    )

    # --- Comparison ---
    delta_B = B_fit - B_TT_pred
    n_sigma = abs(delta_B) / sigma_B_total

    emit(f"\n{'='*60}")
    emit(f"B_TT predicted (QNG) = {B_TT_pred:.6f}")
    emit(f"B_TT fitted  (data)  = {B_fit:.6f}")
    emit(f"Delta                = {delta_B:+.6f}")
    emit(f"sigma_total          = {sigma_B_total:.6f}")
    emit(f"n_sigma              = {n_sigma:.3f}")

    if at_boundary:
        emit("*** WARNING: B fit hit grid boundary — result may be biased high ***")

    crit_n_sigma = n_sigma <= 2.0
    crit_boundary = not at_boundary

    emit(f"\nPass criteria:")
    emit(f"  n_sigma <= 2.0: {'PASS' if crit_n_sigma else 'FAIL'}  ({n_sigma:.3f})")
    emit(f"  B not at grid boundary: {'PASS' if crit_boundary else 'WARN'}  (informational)")

    passed = crit_n_sigma and crit_boundary
    result = "PASS" if passed else "FAIL"
    emit(f"\nRESULT: {result}")

    log.close()

    # CSV
    with open(os.path.join(args.out_dir, "B-comparison.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quantity", "value"])
        w.writeheader()
        for k, v in [
            ("d_s", d_s), ("ell_D_T", ell_D_T), ("ell_D_P", ell_D_P), ("ell_A", ell_A),
            ("B_TT_pred", B_TT_pred), ("B_EE_pred", B_EE_pred), ("B_TE_pred", B_TE_pred),
            ("sigma_B_pred", sigma_B_pred), ("sigma_B_fit", sigma_B_fit),
            ("sigma_B_total", sigma_B_total),
            ("B_TT_fitted", B_fit), ("delta_B", delta_B), ("n_sigma", n_sigma),
        ]:
            w.writerow({"quantity": k, "value": v})

    md = f"""# QNG-T-069 Summary

**Claim:** QNG-C-123 — oscillation amplitude B from spectral dimension
**Result:** {result}
**Date:** {datetime.datetime.utcnow().strftime('%Y-%m-%d')}

## Derivation

In QNG, coherent acoustic oscillations decay over one acoustic period ell_A
under the relaxation damping scale ell_D_T. The preserved fraction is:

    B_TT = exp(-ell_A / ell_D_T) = exp(-2 / d_s)

Because ell_A = 2 × ell_D_T / d_s (from QNG-C-123 A4).

With d_s = {d_s}, ell_D_T = {ell_D_T}:
- ell_A = {ell_A:.3f}
- **B_TT_pred = exp(-2/d_s) = {B_TT_pred:.6f}**
- B_EE_pred = exp(-ell_A/ell_D_P) = {B_EE_pred:.6f}
- B_TE_pred = sqrt(B_TT × B_EE) = {B_TE_pred:.6f}

## Fit Result (TT, fine B grid step=0.025)

| Quantity | Value |
|----------|-------|
| B_TT predicted | {B_TT_pred:.6f} ± {sigma_B_total:.6f} |
| B_TT fitted    | {B_fit:.6f} |
| Delta          | {delta_B:+.6f} |
| n_sigma        | {n_sigma:.3f} |

## Pass Criterion

- Threshold: n_sigma ≤ 2.0
- Achieved: {n_sigma:.3f} sigma
- **{result}**
"""
    with open(os.path.join(args.out_dir, "summary.md"), "w") as f:
        f.write(md)

    print(f"\nOutputs written to {args.out_dir}/")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
