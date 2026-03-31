# G16b Hybrid Promotion Evaluation (v1)

- eval_id: `g16b-hybrid-attack-holdout-v1`
- generated_utc: `2026-03-01T23:52:05.934358Z`
- input_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/g16b-split-hybrid-attack-holdout-v1/summary.csv`
- decision: `PASS`

## Overall

- n=400, v1_pass=314, hybrid_pass=326, improved=12, degraded=0, uplift_pp=3.000

## Criteria Checks

- zero_degraded: true
- per_dataset_nondegrade: true
- high_signal_nondegrade: true
- low_signal_improvement: true
- global_uplift_min(2.000pp): true

## Regime Summary

- low_signal: n=66, v1_fail=20, hybrid_fail=8
- high_signal: n=334, v1_fail=66, hybrid_fail=66

## Per-Dataset

| dataset | n | v1_pass | hybrid_pass | uplift_pp | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-004 | 200 | 157 | 163 | 3.000 | 0 | true |
| DS-008 | 200 | 157 | 163 | 3.000 | 0 | true |

