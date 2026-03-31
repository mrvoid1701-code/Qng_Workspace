# GR Stage-2 G11a-v3 Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-v3-attack-holdout-v1`
- generated_utc: `2026-03-02T09:20:03.714587Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv`
- decision: `PASS`

## Totals

- g11_v2_pass: `394/400`
- g11_v3_pass: `398/400`
- improved_vs_v2: `4`
- degraded_vs_v2: `0`
- weak_corr_fail_count_v2: `6`
- weak_corr_fail_count_v3: `2`
- weak_corr_drop: `4`

## Checks

- zero_degraded: `true`
- improved_min: `true` (min=1)
- per_dataset_nondegrade: `true`
- weak_corr_drop_min: `true` (min=0)

## Dataset Summary

| dataset | n | g11_v2_pass | g11_v3_pass | improved | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-004 | 200 | 197 | 199 | 2 | 0 | true |
| DS-008 | 200 | 197 | 199 | 2 | 0 | true |
