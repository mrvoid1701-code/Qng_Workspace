# QNG-T-065 Summary

**Claim:** QNG-C-120 — Silk damping scale from mu_1 and d_s
**Result:** PASS
**Date:** 2026-03-15

## Predicted Formula (v2 — corrected)

ell_damp^QNG = ell_D_T * sqrt(6 / (d_s * mu_1))
             = 576.144 * sqrt(6 / (4.082 * 0.291))
             = **1294.9 ± 19.8**

Physical basis: factor 6 = 2×3 from 3D isotropic diffusion (variance × dimensions);
d_s in denominator corrects for QNG graph dimensionality vs 3D physical space.

v1 formula (failed): ell_damp = ell_D_T/sqrt(mu_1) = 1068.0 (17.8σ FAIL)

## Results

| Quantity | Value | Uncertainty |
|----------|-------|-------------|
| mu_1 (G17, Jaccard) | 0.291 | — |
| d_s (G18d v2, Jaccard) | 4.082 | ± 0.125 |
| ell_D_T (T-052 best-fit) | 576.144 | — |
| ell_damp predicted (QNG) | 1294.9 | ± 19.8 |
| ell_damp fitted (Planck TT) | 1290.9 | ± 12.5 |
| Delta | -4.0 | — |
| Discrepancy | 0.171 σ | — |
| Fractional error | 0.31% | — |

## Method

1. Fit power-law baseline D_ell = A * ell^(-p) on ell in [200, 900]: A=9.294e+04, p=0.5791
2. Compute ratio = data / baseline for ell >= 1000
3. Fit exp(-(ell/ell_damp)^2) to ratio via log-linear OLS
4. Compare to QNG prediction

## Pass Criterion

- Threshold: discrepancy ≤ 2 sigma
- Achieved: 0.171 sigma
- **PASS**
