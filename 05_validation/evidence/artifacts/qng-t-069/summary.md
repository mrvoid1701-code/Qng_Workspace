# QNG-T-069 Summary

**Claim:** QNG-C-123 — oscillation amplitude B from spectral dimension
**Result:** PASS
**Date:** 2026-03-15

## Derivation

In QNG, coherent acoustic oscillations decay over one acoustic period ell_A
under the relaxation damping scale ell_D_T. The preserved fraction is:

    B_TT = exp(-ell_A / ell_D_T) = exp(-2 / d_s)

Because ell_A = 2 × ell_D_T / d_s (from QNG-C-123 A4).

With d_s = 4.082, ell_D_T = 576.144:
- ell_A = 282.285
- **B_TT_pred = exp(-2/d_s) = 0.612653**
- B_EE_pred = exp(-ell_A/ell_D_P) = 0.779804
- B_TE_pred = sqrt(B_TT × B_EE) = 0.691194

## Fit Result (TT, fine B grid step=0.025)

| Quantity | Value |
|----------|-------|
| B_TT predicted | 0.612653 ± 0.015516 |
| B_TT fitted    | 0.625000 |
| Delta          | +0.012347 |
| n_sigma        | 0.796 |

## Pass Criterion

- Threshold: n_sigma ≤ 2.0
- Achieved: 0.796 sigma
- **PASS**
