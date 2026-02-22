# Model Comparison

| Check | Baseline | Memory | Status |
| --- | --- | --- | --- |
| Sample rows | n=3 | n=3 | pass |
| Sigma weights | published pass-level sigma | same sigma rows | pass |
| Likelihood form | weighted chi-square | weighted chi-square | pass |
| Priors/search space | tau fixed to 0 | tau fitted on same rows | pass |
| Perigee vs whole | dchi2=-2432.777809 | dchi2=-2432.777809 | pass |
| Flyby vs Pioneer domain | tau_flyby=0.013290 | tau_pioneer=3.976562e-04 | fail |
| Pioneer correction stage | raw dchi2=-2442.924722 | corrected dchi2=-2432.542021 | pass |

| Metric | Baseline | Memory | Delta |
| --- | --- | --- | --- |
| chi2_total | 2439.747922 | 6.970113 | -2432.777809 |
| AIC_total | 2439.747922 | 8.970113 | -2430.777809 |
| BIC_total | 2439.747922 | 8.068726 | -2431.679197 |
