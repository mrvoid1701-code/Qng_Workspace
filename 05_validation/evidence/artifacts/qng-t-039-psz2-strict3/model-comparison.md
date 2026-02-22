# Model Comparison

Strict comparability checklist:

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | lensing=485, rotation=3391 | lensing=485, rotation=3391 | pass |
| Sigma weights | Same input sigma (`sigma`, `v_err`) | Same input sigma (`sigma`, `v_err`) | pass |
| Likelihood form | Weighted chi-square over identical rows | Weighted chi-square over identical rows | pass |
| Priors / search space | Null fixed model (`tau=0`, `k=0`) | Same row set; fitted `tau` and `k` with deterministic solver | pass |

Metric comparison:

| Metric | Baseline | Memory | Delta (memory - baseline) |
| --- | --- | --- | --- |
| chi2_lensing | 1.127591e+04 | 0.000000 | -1.127591e+04 |
| chi2_rotation | 1.025646e+06 | 1.569151e+05 | -8.687304e+05 |
| chi2_total | 1.036921e+06 | 1.569151e+05 | -8.800063e+05 |
| delta_chi2_per_point (lensing) | - | - | -23.249297 |
| delta_chi2_per_point (rotation) | - | - | -256.187080 |
| delta_chi2_per_point (total) | - | - | -227.039809 |
| AIC_total | 1.036921e+06 | 1.569191e+05 | -8.800023e+05 |
| BIC_total | 1.036921e+06 | 1.569316e+05 | -8.799898e+05 |
