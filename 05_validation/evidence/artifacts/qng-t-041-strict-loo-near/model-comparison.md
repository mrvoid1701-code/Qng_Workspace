# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-4791.447388 | dchi2=-4791.447388 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.001329 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 1.170691e+04 | 6915.460534 | -4791.447388 |
| AIC_total | 1.170691e+04 | 6917.460534 | -4789.447388 |
| BIC_total | 1.170691e+04 | 6917.252294 | -4789.655629 |
