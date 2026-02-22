# Parameter Stability - QNG P2 Cosmo Suite

- CV threshold: `0.30`

| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| corr_a_vs_n13 | 18 | 0.999429 | 6.655409e-05 | 6.659214e-05 | 0.999290 | 0.999560 | pass |
| corr_complexity_vs_n | 18 | 0.999997 | 2.903348e-06 | 2.903358e-06 | 0.999986 | 0.999999 | pass |
| slope_complexity_vs_n | 18 | 0.312673 | 6.549555e-04 | 0.002095 | 0.311206 | 0.313758 | pass |
| r2_scale | 18 | 0.998836 | 1.361325e-04 | 1.362912e-04 | 0.998581 | 0.999117 | pass |
| mape_scale | 18 | 0.008347 | 4.119011e-04 | 0.049348 | 0.007578 | 0.009056 | pass |
| r2_entropy | 18 | 0.999634 | 3.884754e-05 | 3.886176e-05 | 0.999569 | 0.999702 | pass |
| omega_monotonic_ratio | 18 | 1.000000 | 0.000000 | 0.000000 | 1.000000 | 1.000000 | pass |
| entropy_monotonic_ratio | 18 | 0.954321 | 0.014994 | 0.015711 | 0.922222 | 0.977778 | pass |
| k_entropy_fit | 18 | 1.000101 | 6.896485e-05 | 6.895787e-05 | 0.999970 | 1.000274 | pass |

Interpretation:
- Low CV indicates robust behavior under seed variation.
- `warn` does not automatically fail a test; use with primary fit metrics.
