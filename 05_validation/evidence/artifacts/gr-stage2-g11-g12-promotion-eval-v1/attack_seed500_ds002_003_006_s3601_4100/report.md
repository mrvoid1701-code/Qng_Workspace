# GR Stage-2 G11/G12 Candidate Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-g12-attack-seed500-v1`
- generated_utc: `2026-03-02T01:44:34.930505Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- overall_decision: `FAIL`

## Gate Decisions

- G11: decision=FAIL, v1_pass=1426, v2_pass=1426, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=false, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=1392, v2_pass=1495, improved=103, degraded=0, uplift_pp=6.867, failcase_uplift_pp=95.370
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE2: decision=PASS, v1_pass=1346, v2_pass=1423, improved=77, degraded=0, uplift_pp=5.133, failcase_uplift_pp=50.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 500 | 475 | 475 | 0 | 0 | 0.000 | 0.000 | true |
| G11 | DS-003 | 500 | 462 | 462 | 0 | 0 | 0.000 | 0.000 | true |
| G11 | DS-006 | 500 | 489 | 489 | 0 | 0 | 0.000 | 0.000 | true |
| G12 | DS-002 | 500 | 469 | 498 | 29 | 0 | 5.800 | 93.548 | true |
| G12 | DS-003 | 500 | 455 | 497 | 42 | 0 | 8.400 | 93.333 | true |
| G12 | DS-006 | 500 | 468 | 500 | 32 | 0 | 6.400 | 100.000 | true |
| STAGE2 | DS-002 | 500 | 453 | 474 | 21 | 0 | 4.200 | 44.681 | true |
| STAGE2 | DS-003 | 500 | 430 | 460 | 30 | 0 | 6.000 | 42.857 | true |
| STAGE2 | DS-006 | 500 | 463 | 489 | 26 | 0 | 5.200 | 70.270 | true |

