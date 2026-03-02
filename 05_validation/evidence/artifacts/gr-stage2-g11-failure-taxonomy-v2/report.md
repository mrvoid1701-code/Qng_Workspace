# GR Stage-2 Official G11 Failure Taxonomy (v1)

- generated_utc: `2026-03-02T08:57:26.965949Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv`
- total_profiles_scanned: `600`
- g11_fail_profiles_analyzed: `13`
- taxonomy scope: `strictly g11_status=fail rows`

## Freeze Constants

- weak_corr_threshold: `0.20`
- multi_peak_ratio_threshold: `0.98`
- multi_peak_distance_norm_threshold: `0.10`
- low_signal_quantile (dataset-relative): `0.15`
- sparse_quantile (dataset-relative): `0.10`
- degenerate_quantile (dataset-relative): `0.10`

## Primary Findings

- flag_weak_high_signal_corr: `12/13`
- flag_low_signal: `6/13`
- flag_multi_peak: `6/13`
- flag_sparse_graph: `1/13`
- flag_degenerate_geometry: `2/13`

Top root-cause labels:
- `low_signal_weak_corr`: `6`
- `weak_high_signal_corr`: `4`
- `multi_peak_weak_corr`: `2`
- `g11b_slope_fail`: `1`

## Dataset Breakdown

| dataset | g11_fails | weak_corr | low_signal | multi_peak | sparse_graph | degenerate_geometry |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 3 | 2 | 1 | 2 | 0 | 0 |
| DS-003 | 8 | 8 | 5 | 3 | 1 | 2 |
| DS-006 | 2 | 2 | 0 | 1 | 0 | 0 |

## Outputs

- `g11_fail_cases.csv`
- `dataset_fail_summary.csv`
- `pattern_summary.csv`
- `dataset_thresholds.csv`
- `g11_all_profiles_metrics.csv`
