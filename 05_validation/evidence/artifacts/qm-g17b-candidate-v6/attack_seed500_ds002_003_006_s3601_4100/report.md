# QM G17b Candidate-v6 Report

- generated_utc: `2026-03-05T22:22:15.841731Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v11/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G17b v1 -> v6: `1420/1500 -> 1500/1500`
- G17 v1 -> v6: `1496/1500 -> 1500/1500`
- QM lane v1 -> v6: `1492/1500 -> 1496/1500`
- improved_g17: `4`
- degraded_g17: `0`
- improved_qm_lane: `4`
- degraded_qm_lane: `0`

## Notes

- G17b-v1 pass cases are preserved.
- Recovery uses high-signal median slope across fixed quantile windows.
- Threshold value is unchanged from v1 definition.
- No formula or threshold edits in core gate scripts.
