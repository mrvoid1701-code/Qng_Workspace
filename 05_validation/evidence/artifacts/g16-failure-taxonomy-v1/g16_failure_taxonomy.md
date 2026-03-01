# G16 Failure Taxonomy (v1)

- generated_utc: `2026-03-01T23:01:58.567880Z`
- profiles_total: `60`
- g16_fail: `9`
- g16_pass: `51`
- thresholds/formulas: unchanged (diagnostic-only run)

## Sub-Gate Failure Counts

| subgate | fail_count |
| --- | --- |
| G16a | 0 |
| G16b | 9 |
| G16c | 0 |
| G16d | 0 |

## Failure Signatures

| signature | count |
| --- | --- |
| G16b | 9 |

## Dataset Fail Split

| dataset | fail_count | pass_count | fail_rate |
| --- | --- | --- | --- |
| DS-002 | 3 | 17 | 0.150000 |
| DS-003 | 4 | 16 | 0.200000 |
| DS-006 | 2 | 18 | 0.100000 |

## Pass vs Fail Feature Means

| feature | fail_mean | pass_mean |
| --- | --- | --- |
| mean_degree | 9.151756 | 9.409267 |
| sigma_std | 0.247454 | 0.247375 |
| sigma_cv | 0.464047 | 0.480342 |
| peak2_to_peak1 | 0.990391 | 0.988166 |
| peak12_distance_norm | 0.064235 | 0.071660 |
| closure_rel | 0.000000 | 0.000000 |
| r2_G11_T11 | 0.029640 | 0.103988 |
| m_sq_abs | 0.011765 | 0.013555 |
| hessian_frac_neg | 1.000000 | 1.000000 |

## Pattern Notes

1. `G16b` occurs `9` times; examples: `DS-002/seed3411, DS-002/seed3418`.

