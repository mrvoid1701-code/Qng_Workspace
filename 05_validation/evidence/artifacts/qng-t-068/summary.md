# QNG-T-068 Summary

**Claim:** QNG-C-123 — Full CMB relaxation-surface model TT+TE+EE
**Result:** PASS
**Date:** 2026-03-15

## Model

C_ℓ^QNG = A₀ × ℓ^(−p_D) × exp(−J×ℓ/ℓ_D) × [1 + B×cos(2πℓ/ℓ_A + φ)]

**Fixed from theory (T-052 + G18d):**
- p_D_T = 1.119, ℓ_D_T = 576.144
- p_D_P = 1.119, ℓ_D_P = 1134.984
- ℓ_A predicted = 2×ℓ_D_T/d_s = **282.285** (d_s = 4.082)
- B_TT = exp(−2/d_s) = **0.6127** (from T-069)
- B_EE = exp(−ℓ_A/ℓ_D_P) = **0.7798** (from T-069)
- B_TE = sqrt(B_TT×B_EE) = **0.6912** (from QNG-C-123 A5)

## Fit Results

| Spectrum | A₀ | J | B | φ | χ²_rel |
|----------|-----|---|---|---|--------|
| TT | 7.522e+05 | 0.000 | 0.613 | 2.36 | -13.8281 |
| TE | 2.027e+03 | 2.200 | 0.691 | 2.36 | -0.7374 |
| EE | 2.137e+03 | 2.200 | 0.780 | 1.96 | -1309.7256 |

**Combined χ²_rel = -371.673380**  (T-052 baseline: -22.317414)

## Pass Criteria

| Criterion | Threshold | Achieved | Status |
|-----------|-----------|----------|--------|
| χ²_rel_total | < -22.317414 | -371.6734 | PASS |
| ℓ_A deviation | < 10% | 6.5% | PASS |
| B (theory-fixed) | exp(−2/d_s) | TT=0.6127 EE=0.7798 TE=0.6912 | fixed |

## **PASS**
