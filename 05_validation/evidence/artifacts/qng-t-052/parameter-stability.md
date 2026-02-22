# Parameter Stability - QNG-T-052

- CV threshold: `0.30`
- Grid: memory-window offsets and prominence scaling factors.

| Spectrum | Metric | Samples | Mean | StdDev | CV | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TT | coherence_score | 25 | 0.701714 | 0.213280 | 0.303941 | warn |
| TT | delta_chi2 | 25 | -1047.098430 | 11.231070 | 0.010726 | pass |
| TT | peak_count | 25 | 4.560000 | 2.041176 | 0.447626 | warn |
| TE | coherence_score | 25 | 0.929675 | 0.075999 | 0.081748 | pass |
| TE | delta_chi2 | 25 | -1351.776707 | 13.432566 | 0.009937 | pass |
| TE | peak_count | 25 | 6.720000 | 3.954946 | 0.588534 | warn |
| EE | coherence_score | 25 | 0.941921 | 0.088028 | 0.093456 | pass |
| EE | delta_chi2 | 25 | -1039.471169 | 23.561703 | 0.022667 | pass |
| EE | peak_count | 25 | 11.560000 | 1.416474 | 0.122532 | pass |

Interpretation:
- Lower CV indicates robustness to moderate preprocessing choices.
- `delta_chi2` should remain negative if coherence model consistently improves over baseline.
