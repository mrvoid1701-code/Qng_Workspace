# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-7700.199058 | dchi2=-7700.199058 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002054 | tau_pioneer=3.976562e-04 | pass |
| Pioneer correction stage | raw dchi2=-2442.924722 | corrected dchi2=-2432.542021 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 1.917812e+04 | 1.147792e+04 | -7700.199058 |
| AIC_total | 1.917812e+04 | 1.147992e+04 | -7698.199058 |
| BIC_total | 1.917812e+04 | 1.147971e+04 | -7698.407299 |
