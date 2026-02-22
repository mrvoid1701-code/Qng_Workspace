# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-5847.506332 | dchi2=-5847.506332 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002053 | tau_pioneer=1.196490e-04 | pass |
| Pioneer correction stage | raw dchi2=-4433.542207 | corrected dchi2=-4430.420979 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2.240596e+04 | 1.655845e+04 | -5847.506332 |
| AIC_total | 2.240596e+04 | 1.656045e+04 | -5845.506332 |
| BIC_total | 2.240596e+04 | 1.656025e+04 | -5845.714572 |
