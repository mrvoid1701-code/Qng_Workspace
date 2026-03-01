# G16b Hybrid Promotion Evaluation (v1)

- eval_id: `g16b-hybrid-primary-v1`
- generated_utc: `2026-03-01T23:47:53.016222Z`
- input_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`
- decision: `PASS`

## Overall

- n=600, v1_pass=473, hybrid_pass=516, improved=43, degraded=0, uplift_pp=7.167

## Criteria Checks

- zero_degraded: true
- per_dataset_nondegrade: true
- high_signal_nondegrade: true
- low_signal_improvement: true
- global_uplift_min(2.000pp): true

## Regime Summary

- low_signal: n=210, v1_fail=60, hybrid_fail=17
- high_signal: n=390, v1_fail=67, hybrid_fail=67

## Per-Dataset

| dataset | n | v1_pass | hybrid_pass | uplift_pp | degraded | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 200 | 158 | 172 | 7.000 | 0 | true |
| DS-003 | 200 | 159 | 162 | 1.500 | 0 | true |
| DS-006 | 200 | 156 | 182 | 13.000 | 0 | true |

