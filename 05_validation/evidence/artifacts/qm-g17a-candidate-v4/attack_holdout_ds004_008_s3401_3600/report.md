# QM G17a Candidate-v4 Report

- generated_utc: `2026-03-05T08:50:31.142084Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v9/attack_holdout_ds004_008_s3401_3600/summary.csv`
- profiles: `400`

## Pass Counts

- G17 v1 -> v2: `400/400 -> 400/400`
- QM lane v1 -> v2: `400/400 -> 400/400`
- improved_g17: `0`
- degraded_g17: `0`
- improved_qm_lane: `0`
- degraded_qm_lane: `0`

## Notes

- Candidate applies only to source fail profiles where only G17a blocks G17.
- Uses fixed quantile windows and the same parsed G17a threshold from metric checks.
- No threshold/formula edits in core runners.
