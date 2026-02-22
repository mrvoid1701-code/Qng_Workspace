# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=3 | n=3 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-3268.859687 | dchi2=-3268.859687 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.013290 | tau_pioneer=1.053605e-04 | fail |
| Pioneer correction stage | raw dchi2=-3271.545102 | corrected dchi2=-3268.796518 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 3287.747922 | 18.888236 | -3268.859687 |
| AIC_total | 3287.747922 | 20.888236 | -3266.859687 |
| BIC_total | 3287.747922 | 19.986848 | -3267.761075 |
