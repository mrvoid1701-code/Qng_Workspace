# G16b Hybrid Promotion Evaluation (v1)

- eval_id: `g16b-hybrid-attack-seed500-v1`
- generated_utc: `2026-03-01T23:52:05.925837Z`
- input_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/g16b-split-hybrid-attack-seed500-v1/summary.csv`
- decision: `PASS`

## Overall

- n=1500, v1_pass=1156, hybrid_pass=1266, improved=110, degraded=0, uplift_pp=7.333

## Criteria Checks

- zero_degraded: true
- per_dataset_nondegrade: true
- high_signal_nondegrade: true
- low_signal_improvement: true
- global_uplift_min(2.000pp): true

## Regime Summary

- low_signal: n=538, v1_fail=145, hybrid_fail=35
- high_signal: n=962, v1_fail=199, hybrid_fail=199

## Per-Dataset

| dataset | n | v1_pass | hybrid_pass | uplift_pp | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 500 | 398 | 422 | 4.800 | 0 | true |
| DS-003 | 500 | 375 | 386 | 2.200 | 0 | true |
| DS-006 | 500 | 383 | 458 | 15.000 | 0 | true |

