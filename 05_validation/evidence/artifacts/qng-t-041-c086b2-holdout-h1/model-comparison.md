# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=3 | n=3 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-4408.640312 | dchi2=-4408.640312 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.013290 | tau_pioneer=1.194253e-04 | fail |
| Pioneer correction stage | raw dchi2=-4408.568748 | corrected dchi2=-4408.568748 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 5654.000000 | 1245.359688 | -4408.640312 |
| AIC_total | 5654.000000 | 1247.359688 | -4406.640312 |
| BIC_total | 5654.000000 | 1246.458300 | -4407.541700 |
