# QM G18 Candidate-v5 Report

- generated_utc: `2026-03-05T08:14:11.552320Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v7/attack_holdout_ds004_008_s3401_3600/summary.csv`
- profiles: `400`

## Pass Counts

- G18 v1 -> v5: `382/400 -> 396/400`
- QM lane v1 -> v5: `382/400 -> 396/400`
- improved_g18: `14`
- degraded_g18: `0`
- improved_qm_lane: `14`
- degraded_qm_lane: `0`

## Notes

- G18d-v1 is preserved when already pass.
- G18d-v5 applies fixed multi-window local spectral-dimension peak-envelope recovery on G18d-v1 fail cases.
- Threshold band for G18d remains unchanged from v1.
