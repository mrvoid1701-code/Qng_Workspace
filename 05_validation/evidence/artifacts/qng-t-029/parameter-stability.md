# Parameter Stability - QNG-T-029

- CV threshold: `0.30`

| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tau_fit | 12 | 1.408333 | 0.221579 | 0.157334 | 1.000000 | 1.700000 | pass |
| k_memory_fit | 12 | 0.816667 | 0.074536 | 0.091268 | 0.650000 | 0.850000 | pass |
| g_base_fit | 12 | 1.150000 | 0.051962 | 0.045184 | 1.060000 | 1.180000 | pass |

Interpretation:
- Low CV indicates robust parameter recovery across seeds.
- `warn` means fit variability should be reviewed before publication-grade claims.
