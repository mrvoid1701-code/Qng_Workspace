# Rotation Baseline Upgrade Check

| Check | Flexible baseline | Memory model | Status |
| --- | --- | --- | --- |
| Sample rows | n=3391 | n=3391 | pass |
| Sigma weights | same `v_err` rows | same `v_err` rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Free parameters | 1 (`a_flex`) | 1 (`k_memory`) | pass |
| Priors | `a_flex >= 0` | `k_memory >= 0` | pass |

| Metric | Flexible baseline | Memory | Delta (memory - flex) |
| --- | --- | --- | --- |
| chi2_rotation | 6.008261e+05 | 1.569151e+05 | -4.439109e+05 |
| AIC_rotation | 6.008281e+05 | 1.569171e+05 | -4.439109e+05 |
| BIC_rotation | 6.008342e+05 | 1.569232e+05 | -4.439109e+05 |
| delta_chi2_per_point | - | - | -130.908564 |

Interpretation:
- Flexible baseline fit parameter: `a_flex=5863.869799`.
- Memory fit parameter: `k_memory=1.000000`.
- Memory beats flexible baseline: `true`.
