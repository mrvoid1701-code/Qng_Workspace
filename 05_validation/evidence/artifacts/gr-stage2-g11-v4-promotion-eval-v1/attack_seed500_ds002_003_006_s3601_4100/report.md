# GR Stage-2 G11a-v4 Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-v4-attack-seed500-v1`
- generated_utc: `2026-03-02T10:06:57.799815Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- decision: `PASS`

## Totals

- g11_v3_pass: `1464/1500`
- g11_v4_pass: `1470/1500`
- g11_v3_fail -> g11_v4_fail: `36 -> 30`
- improved_vs_v3: `6`
- degraded_vs_v3: `0`
- stage2_v3_pass -> stage2_v4_pass: `1460/1500 -> 1466/1500`
- stage2_improved: `6`
- stage2_degraded: `0`

## Checks

- zero_degraded: `true`
- improved_min: `true` (min=0)
- per_dataset_nondegrade: `true`
- max_fails_after: `true` (max=-1)

## Dataset Summary

| dataset | n | g11_v3_pass | g11_v4_pass | improved | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 500 | 491 | 491 | 0 | 0 | true |
| DS-003 | 500 | 478 | 483 | 5 | 0 | true |
| DS-006 | 500 | 495 | 496 | 1 | 0 | true |
