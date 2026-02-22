# Parameter Stability - Core Closure v1 Volume Rules

| Rule | Metric | Samples | Mean | StdDev | CV | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V-A | n_slope | 12 | -0.434692 | 0.074735 | 0.171926 | -0.557544 | -0.284288 |
| V-A | v_slope | 12 | 1.646472e-17 | 6.393155e-17 | inf | -9.898966e-17 | 9.398554e-17 |
| V-A | v_drift_rel | 12 | 1.200291e-15 | 3.000290e-16 | 0.249964 | 8.121269e-16 | 1.795015e-15 |
| V-A | jsd_mean | 12 | 0.283717 | 0.096351 | 0.339601 | 0.171731 | 0.459042 |
| V-A | attractor_overlap | 12 | 0.189941 | 0.131433 | 0.691966 | 0.000000 | 0.411765 |
| V-A | gr_ratio_tau0_vs_nom | 12 | 1.660742e-05 | 1.965027e-07 | 0.011832 | 1.595569e-05 | 1.666667e-05 |
| V-A | gr_tau0_max | 12 | 2.453858e-21 | 3.884370e-22 | inf | 1.595569e-21 | 3.253799e-21 |
| V-B | n_slope | 12 | 126.143537 | 9.590138 | 0.076026 | 112.692502 | 139.625560 |
| V-B | v_slope | 12 | 13.775469 | 2.833612 | 0.205700 | 9.084187 | 18.068622 |
| V-B | v_drift_rel | 12 | 36.685541 | 1.655457 | 0.045126 | 34.207332 | 40.409093 |
| V-B | jsd_mean | 12 | 0.003827 | 0.001283 | 0.335185 | 0.002862 | 0.007652 |
| V-B | attractor_overlap | 12 | 0.105765 | 0.013712 | 0.129642 | 0.084350 | 0.125980 |
| V-B | gr_ratio_tau0_vs_nom | 12 | 1.666667e-05 | 1.467104e-21 | 8.802625e-17 | 1.666667e-05 | 1.666667e-05 |
| V-B | gr_tau0_max | 12 | 5.753628e-06 | 4.958981e-07 | 0.086189 | 4.978431e-06 | 6.908411e-06 |

Notes:
- `V-A` expects low `v_drift_rel` and low `jsd_mean`.
- `V-B` expects positive growth (`n_slope`, `v_slope`) with controlled spectral drift.
- GR-kill metrics should remain near zero in `tau -> 0` proxy.
