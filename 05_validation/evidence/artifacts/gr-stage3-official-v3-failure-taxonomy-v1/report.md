# GR Stage-3 Failure Taxonomy (v1)

- generated_utc: `2026-03-02T13:54:51.907906Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv`
- profiles_total: `600`
- strict_fail_scope: `3` (only `stage3_status=fail` rows classified)

## Fail Pattern Counts

- `G11`: `3`

## Cause Classes

- `g11b_slope_instability`: `1`
- `weak_corr_multi_peak`: `1`
- `weak_corr_sparse_graph`: `1`

## Top Feature Correlations (Stage3 Fail)

- `g11b_value`: corr_stage3_fail=`-0.171796`, delta_fail_minus_pass=`-1.711070`
- `g11a_value`: corr_stage3_fail=`-0.124388`, delta_fail_minus_pass=`-0.096249`
- `g12d_value`: corr_stage3_fail=`0.122299`, delta_fail_minus_pass=`0.162872`
- `g12c_value`: corr_stage3_fail=`-0.113836`, delta_fail_minus_pass=`-0.201702`
- `sigma_peak2_to_peak1`: corr_stage3_fail=`0.072786`, delta_fail_minus_pass=`0.009157`
- `radial_min_bin_count`: corr_stage3_fail=`-0.033907`, delta_fail_minus_pass=`-0.864322`
- `graph_density`: corr_stage3_fail=`0.020842`, delta_fail_minus_pass=`0.000230`
- `mean_abs_u`: corr_stage3_fail=`-0.010412`, delta_fail_minus_pass=`-0.000871`
- `var_u`: corr_stage3_fail=`-0.008353`, delta_fail_minus_pass=`-0.000008`
- `peak12_distance_norm`: corr_stage3_fail=`0.006219`, delta_fail_minus_pass=`0.003524`

## Notes

- This is diagnostic-only; no thresholds/formulas were changed.
- `low_signal` and `sparse_graph` are percentile labels (P25) for comparative taxonomy only.
- Any further estimator-policy updates should be preregistered before rerun/promotion.
