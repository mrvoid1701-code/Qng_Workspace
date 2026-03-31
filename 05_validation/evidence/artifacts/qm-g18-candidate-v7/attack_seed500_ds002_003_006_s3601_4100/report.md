# QM G18 Candidate-v6 Report

- generated_utc: `2026-03-05T09:06:51.578767Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g19-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- profiles: `1500`

## Pass Counts

- G18 v1 -> v6: `1489/1500 -> 1499/1500`
- QM lane v1 -> v6: `1483/1500 -> 1492/1500`
- improved_g18: `10`
- degraded_g18: `0`
- improved_qm_lane: `9`
- degraded_qm_lane: `0`

## Notes

- G18d-v1 is preserved when already pass.
- G18d-v6 applies fixed multi-scale basin + multi-window local spectral-dimension peak-envelope recovery on source-official fail cases.
- Threshold band for G18d remains unchanged from v1.
