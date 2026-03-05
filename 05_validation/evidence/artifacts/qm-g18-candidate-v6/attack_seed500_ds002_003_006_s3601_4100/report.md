# QM G18 Candidate-v6 Report

- generated_utc: `2026-03-05T08:30:13.159154Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v8/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G18 v1 -> v6: `1467/1500 -> 1489/1500`
- QM lane v1 -> v6: `1453/1500 -> 1475/1500`
- improved_g18: `22`
- degraded_g18: `0`
- improved_qm_lane: `22`
- degraded_qm_lane: `0`

## Notes

- G18d-v1 is preserved when already pass.
- G18d-v6 applies fixed multi-scale basin + multi-window local spectral-dimension peak-envelope recovery on source-official fail cases.
- Threshold band for G18d remains unchanged from v1.
