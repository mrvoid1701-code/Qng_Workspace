# QM G17a Candidate-v4 Report

- generated_utc: `2026-03-05T08:50:33.863486Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v9/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G17 v1 -> v2: `1492/1500 -> 1496/1500`
- QM lane v1 -> v2: `1475/1500 -> 1479/1500`
- improved_g17: `4`
- degraded_g17: `0`
- improved_qm_lane: `4`
- degraded_qm_lane: `0`

## Notes

- Candidate applies only to source fail profiles where only G17a blocks G17.
- Uses fixed quantile windows and the same parsed G17a threshold from metric checks.
- No threshold/formula edits in core runners.
