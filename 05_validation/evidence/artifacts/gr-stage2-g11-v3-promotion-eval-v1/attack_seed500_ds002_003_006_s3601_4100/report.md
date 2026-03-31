# GR Stage-2 G11a-v3 Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-v3-attack-seed500-v1`
- generated_utc: `2026-03-02T09:19:54.275967Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- decision: `PASS`

## Totals

- g11_v2_pass: `1451/1500`
- g11_v3_pass: `1464/1500`
- improved_vs_v2: `13`
- degraded_vs_v2: `0`
- weak_corr_fail_count_v2: `47`
- weak_corr_fail_count_v3: `35`
- weak_corr_drop: `12`

## Checks

- zero_degraded: `true`
- improved_min: `true` (min=1)
- per_dataset_nondegrade: `true`
- weak_corr_drop_min: `true` (min=1)

## Dataset Summary

| dataset | n | g11_v2_pass | g11_v3_pass | improved | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 500 | 485 | 491 | 6 | 0 | true |
| DS-003 | 500 | 473 | 478 | 5 | 0 | true |
| DS-006 | 500 | 493 | 495 | 2 | 0 | true |
