# QM G18 Candidate-v5 Report

- generated_utc: `2026-03-05T08:14:42.829443Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v7/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G18 v1 -> v5: `1440/1500 -> 1467/1500`
- QM lane v1 -> v5: `1426/1500 -> 1453/1500`
- improved_g18: `27`
- degraded_g18: `0`
- improved_qm_lane: `27`
- degraded_qm_lane: `0`

## Notes

- G18d-v1 is preserved when already pass.
- G18d-v5 applies fixed multi-window local spectral-dimension peak-envelope recovery on G18d-v1 fail cases.
- Threshold band for G18d remains unchanged from v1.
