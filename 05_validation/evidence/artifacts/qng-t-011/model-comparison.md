# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=7 | n=7 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5849.361782 | dchi2=-5849.361782 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002054 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.242712e+04 | 1.657776e+04 | -5849.361782 |
| AIC_total | 2.242712e+04 | 1.657976e+04 | -5847.361782 |
| BIC_total | 2.242712e+04 | 1.657971e+04 | -5847.415871 |
