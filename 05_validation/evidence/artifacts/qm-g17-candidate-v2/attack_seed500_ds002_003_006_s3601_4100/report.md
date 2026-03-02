# QM G17 Candidate-v2 Report

- generated_utc: `2026-03-02T19:44:04.517309Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/combined_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G17 v1 -> v2: `1092/1500 -> 1416/1500`
- QM lane v1 -> v2: `1017/1500 -> 1255/1500`
- improved_g17: `324`
- degraded_g17: `0`
- improved_qm_lane: `238`
- degraded_qm_lane: `0`

## Notes

- G17a-v1 global-gap diagnostic is treated as valid in single-well/single-peak regimes.
- G17-v2 preserves v1 behavior in that regime and applies local-gap recovery only under multi-peak mixing.
- No threshold tuning was applied in core runners; this is an observable-definition hardening at governance layer.
