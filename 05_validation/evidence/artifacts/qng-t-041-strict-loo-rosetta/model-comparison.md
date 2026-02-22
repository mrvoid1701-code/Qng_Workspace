# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5338.919450 | dchi2=-5338.919450 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002204 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 1.882712e+04 | 1.348820e+04 | -5338.919450 |
| AIC_total | 1.882712e+04 | 1.349020e+04 | -5336.919450 |
| BIC_total | 1.882712e+04 | 1.348999e+04 | -5337.127690 |
