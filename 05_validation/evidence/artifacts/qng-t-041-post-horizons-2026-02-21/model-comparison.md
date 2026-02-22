# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=9 | n=9 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5849.293279 | dchi2=-5849.293279 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002051 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.242712e+04 | 1.657783e+04 | -5849.293279 |
| AIC_total | 2.242712e+04 | 1.657983e+04 | -5847.293279 |
| BIC_total | 2.242712e+04 | 1.658002e+04 | -5847.096054 |
