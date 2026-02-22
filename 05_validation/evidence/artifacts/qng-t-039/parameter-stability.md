# Parameter Stability - QNG-T-039

- Data source mode: `provided`
- CV threshold: `0.30`

| Parameter | Samples | Mean | StdDev | CV | Threshold | Status |
| --- | --- | --- | --- | --- | --- | --- |
| tau | 24 | 0.999972 | 1.124844e-05 | 1.124876e-05 | < 0.30 | pass |
| k_memory | 24 | 1.000000 | 0.000000 | 0.000000 | < 0.30 | pass |

Interpretation:
- Lower CV means better parameter stability under subsampling.
- If synthetic/mixed data is used, treat these values as pipeline diagnostics, not publication evidence.
