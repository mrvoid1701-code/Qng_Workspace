# Parameter Stability - QNG-T-027

- Data source mode: `provided`
- CV threshold: `0.30`

| Parameter | Samples | Mean | StdDev | CV | Threshold | Status |
| --- | --- | --- | --- | --- | --- | --- |
| tau | 24 | 1.000000 | 0.000000 | 0.000000 | < 0.30 | pass |
| k_memory | 24 | 1.000000 | 0.000000 | 0.000000 | < 0.30 | pass |

Interpretation:
- Lower CV means better parameter stability under subsampling.
- If synthetic/mixed data is used, treat these values as pipeline diagnostics, not publication evidence.
