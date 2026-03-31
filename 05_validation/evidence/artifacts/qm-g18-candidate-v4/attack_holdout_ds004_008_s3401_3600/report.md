# QM G18 Candidate-v4 Report

- generated_utc: `2026-03-05T07:53:19.229457Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/summary.csv`
- profiles: `400`

## Pass Counts

- G18 v1 -> v4: `360/400 -> 382/400`
- QM lane v1 -> v4: `372/400 -> 382/400`
- improved_g18: `22`
- degraded_g18: `0`
- improved_qm_lane: `10`
- degraded_qm_lane: `0`

## Notes

- G18d-v1 is preserved when already pass.
- G18d-v4 applies peak-envelope local spectral-dimension recovery on all G18d-v1 fail cases.
- Threshold band for G18d remains unchanged from v1.
