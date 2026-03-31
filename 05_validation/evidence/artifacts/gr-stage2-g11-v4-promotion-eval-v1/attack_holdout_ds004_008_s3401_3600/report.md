# GR Stage-2 G11a-v4 Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-v4-attack-holdout-v1`
- generated_utc: `2026-03-02T10:06:57.797806Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_holdout_ds004_008_s3401_3600/summary.csv`
- decision: `PASS`

## Totals

- g11_v3_pass: `398/400`
- g11_v4_pass: `398/400`
- g11_v3_fail -> g11_v4_fail: `2 -> 2`
- improved_vs_v3: `0`
- degraded_vs_v3: `0`
- stage2_v3_pass -> stage2_v4_pass: `398/400 -> 398/400`
- stage2_improved: `0`
- stage2_degraded: `0`

## Checks

- zero_degraded: `true`
- improved_min: `true` (min=0)
- per_dataset_nondegrade: `true`
- max_fails_after: `true` (max=-1)

## Dataset Summary

| dataset | n | g11_v3_pass | g11_v4_pass | improved | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-004 | 200 | 199 | 199 | 0 | 0 | true |
| DS-008 | 200 | 199 | 199 | 0 | 0 | true |
