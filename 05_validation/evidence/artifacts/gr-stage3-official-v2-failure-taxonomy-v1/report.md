# GR Stage-3 Failure Taxonomy (v1)

- generated_utc: `2026-03-02T12:47:30.043748Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv`
- profiles_total: `600`
- strict_fail_scope: `8` (only `stage3_status=fail` rows classified)

## Fail Pattern Counts

- `G11`: `7`
- `G12`: `1`

## Cause Classes

- `weak_corr_multi_peak`: `3`
- `weak_corr_sparse_graph`: `2`
- `g11b_slope_instability`: `1`
- `slope_instability`: `1`
- `weak_corr_low_signal`: `1`

## Top Feature Correlations (Stage3 Fail)

- `g11b_value`: corr_stage3_fail=`-0.256070`, delta_fail_minus_pass=`-1.568393`
- `g11a_value`: corr_stage3_fail=`-0.195468`, delta_fail_minus_pass=`-0.093012`
- `g12d_value`: corr_stage3_fail=`0.186719`, delta_fail_minus_pass=`0.152916`
- `g12c_value`: corr_stage3_fail=`-0.183085`, delta_fail_minus_pass=`-0.199492`
- `graph_density`: corr_stage3_fail=`0.029313`, delta_fail_minus_pass=`0.000199`
- `var_u`: corr_stage3_fail=`-0.026034`, delta_fail_minus_pass=`-0.000015`
- `radial_min_bin_count`: corr_stage3_fail=`-0.025970`, delta_fail_minus_pass=`-0.407095`
- `peak12_distance_norm`: corr_stage3_fail=`0.018904`, delta_fail_minus_pass=`0.006586`
- `mean_degree`: corr_stage3_fail=`-0.014030`, delta_fail_minus_pass=`-0.110904`
- `sigma_peak2_to_peak1`: corr_stage3_fail=`0.005787`, delta_fail_minus_pass=`0.000448`

## Notes

- This is diagnostic-only; no thresholds/formulas were changed.
- `low_signal` and `sparse_graph` are percentile labels (P25) for comparative taxonomy only.
- Any further estimator-policy updates should be preregistered before rerun/promotion.
