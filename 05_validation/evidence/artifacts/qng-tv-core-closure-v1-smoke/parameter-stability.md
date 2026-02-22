# Parameter Stability - Core Closure v1 Volume Rules

| Rule | Metric | Samples | Mean | StdDev | CV | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V-A | n_slope | 8 | -0.452607 | 0.062397 | 0.137862 | -0.557544 | -0.358934 |
| V-A | v_slope | 8 | -4.831570e-18 | 6.710361e-17 | inf | -9.898966e-17 | 9.398554e-17 |
| V-A | v_drift_rel | 8 | 1.195129e-15 | 2.612488e-16 | 0.218595 | 8.121269e-16 | 1.633131e-15 |
| V-A | jsd_mean | 8 | 0.289301 | 0.096146 | 0.332340 | 0.172808 | 0.459042 |
| V-A | attractor_overlap | 8 | 0.201579 | 0.107781 | 0.534685 | 0.090909 | 0.411765 |
| V-A | gr_ratio_tau0_vs_nom | 8 | 1.666667e-05 | 1.640272e-21 | 9.841633e-17 | 1.666667e-05 | 1.666667e-05 |
| V-A | gr_tau0_max | 8 | 2.541368e-21 | 3.370121e-22 | inf | 2.225268e-21 | 3.253799e-21 |
| V-B | n_slope | 8 | 127.576320 | 8.768107 | 0.068728 | 113.926645 | 139.625560 |
| V-B | v_slope | 8 | 14.094957 | 2.447205 | 0.173623 | 11.334539 | 17.609991 |
| V-B | v_drift_rel | 8 | 36.497123 | 1.354123 | 0.037102 | 34.207332 | 38.472587 |
| V-B | jsd_mean | 8 | 0.003606 | 5.999058e-04 | 0.166362 | 0.002895 | 0.004647 |
| V-B | attractor_overlap | 8 | 0.108878 | 0.013821 | 0.126940 | 0.089505 | 0.125980 |
| V-B | gr_ratio_tau0_vs_nom | 8 | 1.666667e-05 | 1.120519e-21 | 6.723116e-17 | 1.666667e-05 | 1.666667e-05 |
| V-B | gr_tau0_max | 8 | 5.834097e-06 | 5.438467e-07 | 0.093219 | 4.978431e-06 | 6.908411e-06 |

Notes:
- `V-A` expects low `v_drift_rel` and low `jsd_mean`.
- `V-B` expects positive growth (`n_slope`, `v_slope`) with controlled spectral drift.
- GR-kill metrics should remain near zero in `tau -> 0` proxy.
