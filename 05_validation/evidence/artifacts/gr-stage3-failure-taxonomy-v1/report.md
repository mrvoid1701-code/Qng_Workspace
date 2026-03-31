# GR Stage-3 Failure Taxonomy (v1)

- generated_utc: `2026-03-02T11:12:19.512742Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv`
- profiles_total: `600`
- strict_fail_scope: `30` (only `stage3_status=fail` rows classified)

## Fail Pattern Counts

- `G11`: `15`
- `G12`: `11`
- `G11+G12`: `4`

## Cause Classes

- `weak_corr_multi_peak`: `6`
- `weak_corr_sparse_graph`: `6`
- `slope_instability_binning_edge`: `5`
- `coupled_weakcorr_slope`: `4`
- `slope_instability_low_signal`: `4`
- `slope_instability`: `2`
- `weak_corr_high_signal`: `2`
- `weak_corr_low_signal`: `1`

## Top Feature Correlations (Stage3 Fail)

- `g11b_value`: corr_stage3_fail=`-0.385398`, delta_fail_minus_pass=`-1.242264`
- `g12d_value`: corr_stage3_fail=`0.376109`, delta_fail_minus_pass=`0.162102`
- `g11a_value`: corr_stage3_fail=`-0.316945`, delta_fail_minus_pass=`-0.079369`
- `g12c_value`: corr_stage3_fail=`-0.253818`, delta_fail_minus_pass=`-0.145547`
- `peak12_distance_norm`: corr_stage3_fail=`0.085422`, delta_fail_minus_pass=`0.015663`
- `radial_min_bin_count`: corr_stage3_fail=`-0.084215`, delta_fail_minus_pass=`-0.694737`
- `mean_degree`: corr_stage3_fail=`-0.083188`, delta_fail_minus_pass=`-0.346067`
- `graph_density`: corr_stage3_fail=`0.080727`, delta_fail_minus_pass=`0.000288`
- `var_u`: corr_stage3_fail=`-0.066869`, delta_fail_minus_pass=`-0.000020`
- `mean_abs_u`: corr_stage3_fail=`0.061012`, delta_fail_minus_pass=`0.001652`

## Notes

- This is diagnostic-only; no thresholds/formulas were changed.
- `low_signal` and `sparse_graph` are percentile labels (P25) for comparative taxonomy only.
- Candidate-v2 definitions should be preregistered before any rerun/promotion attempt.
