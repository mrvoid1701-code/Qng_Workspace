# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5825.235074 | dchi2=-5825.235074 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002054 | tau_pioneer=1.194253e-04 | pass |
| Pioneer correction stage | raw dchi2=-4408.568748 | corrected dchi2=-4408.568748 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.239237e+04 | 1.656714e+04 | -5825.235074 |
| AIC_total | 2.239237e+04 | 1.656914e+04 | -5823.235074 |
| BIC_total | 2.239237e+04 | 1.656893e+04 | -5823.443314 |
