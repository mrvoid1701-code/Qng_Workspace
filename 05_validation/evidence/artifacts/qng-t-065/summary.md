# QNG-T-065 Summary

**Claim:** QNG-C-120 — Silk damping scale from mu_1 and d_s
**Result:** FAIL
**Date:** 2026-03-15

## Predicted Formula

ell_damp^QNG = ell_D_T * sqrt(d_s) / (2 * sqrt(mu_1))
             = 576.144 * sqrt(4.082) / (2 * sqrt(0.291))
             = **1068.0 ± 0.0**

## Results

| Quantity | Value | Uncertainty |
|----------|-------|-------------|
| mu_1 (G17, Jaccard) | 0.291 | — |
| d_s (G18d v2, Jaccard) | 4.082 | ± 0.125 |
| ell_D_T (T-052 best-fit) | 576.144 | — |
| ell_damp predicted (QNG) | 1068.0 | ± 0.0 |
| ell_damp fitted (Planck TT) | 1290.9 | ± 12.5 |
| Delta | +222.8 | — |
| Discrepancy | 17.796 σ | — |
| Fractional error | 17.26% | — |

## Method

1. Fit power-law baseline D_ell = A * ell^(-p) on ell in [200, 900]: A=9.294e+04, p=0.5791
2. Compute ratio = data / baseline for ell >= 1000
3. Fit exp(-(ell/ell_damp)^2) to ratio via log-linear OLS
4. Compare to QNG prediction

## Pass Criterion

- Threshold: discrepancy ≤ 2 sigma
- Achieved: 17.796 sigma
- **FAIL**
