# GR Stage-2 G11/G12 Candidate Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-g12-attack-seed500-v2`
- generated_utc: `2026-03-02T08:24:07.242426Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=1426, v2_pass=1451, improved=25, degraded=0, uplift_pp=1.667, failcase_uplift_pp=33.784
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=1392, v2_pass=1495, improved=103, degraded=0, uplift_pp=6.867, failcase_uplift_pp=95.370
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE2: decision=PASS, v1_pass=1346, v2_pass=1447, improved=101, degraded=0, uplift_pp=6.733, failcase_uplift_pp=65.584
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 500 | 475 | 485 | 10 | 0 | 2.000 | 40.000 | true |
| G11 | DS-003 | 500 | 462 | 473 | 11 | 0 | 2.200 | 28.947 | true |
| G11 | DS-006 | 500 | 489 | 493 | 4 | 0 | 0.800 | 36.364 | true |
| G12 | DS-002 | 500 | 469 | 498 | 29 | 0 | 5.800 | 93.548 | true |
| G12 | DS-003 | 500 | 455 | 497 | 42 | 0 | 8.400 | 93.333 | true |
| G12 | DS-006 | 500 | 468 | 500 | 32 | 0 | 6.400 | 100.000 | true |
| STAGE2 | DS-002 | 500 | 453 | 483 | 30 | 0 | 6.000 | 63.830 | true |
| STAGE2 | DS-003 | 500 | 430 | 471 | 41 | 0 | 8.200 | 58.571 | true |
| STAGE2 | DS-006 | 500 | 463 | 493 | 30 | 0 | 6.000 | 81.081 | true |

