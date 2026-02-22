# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5970.164417 | dchi2=-5970.164417 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002274 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.002612e+04 | 1.405596e+04 | -5970.164417 |
| AIC_total | 2.002612e+04 | 1.405796e+04 | -5968.164417 |
| BIC_total | 2.002612e+04 | 1.405775e+04 | -5968.372658 |
