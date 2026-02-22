# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-4539.644615 | dchi2=-4539.644615 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002054 | tau_pioneer=1.053605e-04 | pass |
| Pioneer correction stage | raw dchi2=-3271.545102 | corrected dchi2=-3268.796518 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.002612e+04 | 1.548648e+04 | -4539.644615 |
| AIC_total | 2.002612e+04 | 1.548848e+04 | -4537.644615 |
| BIC_total | 2.002612e+04 | 1.548827e+04 | -4537.852856 |
