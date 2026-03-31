# QM G17 Candidate-v2 Report

- generated_utc: `2026-03-02T19:40:30.150546Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/combined_ds004_008_s3401_3600/summary.csv`
- profiles: `400`

## Pass Counts

- G17 v1 -> v2: `356/400 -> 400/400`
- QM lane v1 -> v2: `322/400 -> 360/400`
- improved_g17: `44`
- degraded_g17: `0`
- improved_qm_lane: `38`
- degraded_qm_lane: `0`

## Notes

- G17a-v1 global-gap diagnostic is treated as valid in single-well/single-peak regimes.
- G17-v2 preserves v1 behavior in that regime and applies local-gap recovery only under multi-peak mixing.
- No threshold tuning was applied in core runners; this is an observable-definition hardening at governance layer.
