# G16 Failure Taxonomy (v1)

- generated_utc: `2026-03-01T23:13:59.370852Z`
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

## G16b Cause Hints

| cause_hint | count |
| --- | --- |
| low_signal_t11 | 7 |
| borderline_linear_fit | 1 |
| weak_coupling | 1 |

## G16b Issue Axes (A/B)

| issue_axis | count |
| --- | --- |
| A_t11_discretization_noise | 7 |
| A_or_B_borderline | 1 |
| A_or_B_weak_alignment | 1 |

## Dataset Fail Split

| dataset | fail_count | pass_count | fail_rate |
| --- | --- | --- | --- |
| DS-002 | 3 | 17 | 0.150000 |
| DS-003 | 4 | 16 | 0.200000 |
| DS-006 | 2 | 18 | 0.100000 |

## Pass vs Fail Means (G16b Diagnostics)

| feature | fail_mean | pass_mean |
| --- | --- | --- |
| t11_std_to_abs_mean | 28.067411 | 36.695129 |
| pearson_r | -0.160354 | -0.318609 |
| spearman_rho | -0.206824 | -0.284264 |
| r2_G11_T11 | 0.029640 | 0.103988 |
| r2_high_signal | 0.129362 | 0.314775 |
| mean_degree | 9.151756 | 9.409267 |
| sigma_std | 0.247454 | 0.247375 |
| peak2_to_peak1 | 0.990391 | 0.988166 |
| peak12_distance_norm | 0.064235 | 0.071660 |

## Pattern Notes

1. `low_signal_t11` appears `7` times; examples: `DS-002/seed3418, DS-002/seed3420`.
2. `borderline_linear_fit` appears `1` times; examples: `DS-003/seed3414`.
3. `weak_coupling` appears `1` times; examples: `DS-002/seed3411`.

