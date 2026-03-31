# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=6 | n=6 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-1.170840e+04 | dchi2=-1.170840e+04 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.002051 | tau_pioneer=0.000000 | pass |
| Pioneer correction stage | raw dchi2=nan | corrected dchi2=nan | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 1.674237e+04 | 5033.969230 | -1.170840e+04 |
| AIC_total | 1.674237e+04 | 5035.969230 | -1.170640e+04 |
| BIC_total | 1.674237e+04 | 5035.760990 | -1.170661e+04 |
