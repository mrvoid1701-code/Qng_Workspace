# GR Stage-2 G11a-v4 Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-v4-primary-v1`
- generated_utc: `2026-03-02T10:05:06.637694Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/primary_ds002_003_006_s3401_3600/summary.csv`
- decision: `PASS`

## Totals

- g11_v3_pass: `594/600`
- g11_v4_pass: `597/600`
- g11_v3_fail -> g11_v4_fail: `6 -> 3`
- improved_vs_v3: `3`
- degraded_vs_v3: `0`
- stage2_v3_pass -> stage2_v4_pass: `594/600 -> 597/600`
- stage2_improved: `3`
- stage2_degraded: `0`

## Checks

- zero_degraded: `true`
- improved_min: `true` (min=2)
- per_dataset_nondegrade: `true`
- max_fails_after: `true` (max=3)

## Dataset Summary

| dataset | n | g11_v3_pass | g11_v4_pass | improved | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 200 | 199 | 199 | 0 | 0 | true |
| DS-003 | 200 | 197 | 200 | 3 | 0 | true |
| DS-006 | 200 | 198 | 198 | 0 | 0 | true |
