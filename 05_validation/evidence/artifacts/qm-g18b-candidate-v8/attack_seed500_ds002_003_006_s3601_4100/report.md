# QM G18b Candidate-v8 Report

- generated_utc: `2026-03-05T23:11:37.533208Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v12/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G18 v1 -> v2: `1499/1500 -> 1500/1500`
- QM lane v1 -> v2: `1496/1500 -> 1497/1500`
- improved_g18: `1`
- degraded_g18: `0`
- improved_qm_lane: `1`
- degraded_qm_lane: `0`

## Notes

- G18 pass rows are preserved unchanged.
- Recovery path targets G18b only and keeps the same parsed threshold from metric checks.
- G18d uses already-frozen v2 status from source summary.
- No threshold/formula edits in core gate scripts.
