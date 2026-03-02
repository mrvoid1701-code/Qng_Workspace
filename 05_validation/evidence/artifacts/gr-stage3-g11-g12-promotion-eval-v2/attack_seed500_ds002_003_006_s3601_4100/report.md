# GR Stage-3 G11/G12 Candidate-v3 Promotion Eval

- eval_id: `gr-stage3-g11-g12-attack-seed500-v3`
- generated_utc: `2026-03-02T13:13:34.451813Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- overall_decision: `PASS`

## Gate Decisions (official-v2 -> candidate-v3)

- G11: decision=PASS, v2_pass=1450, v3_pass=1467, improved=17, degraded=0, uplift_pp=1.133, failcase_uplift_pp=34.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v2_pass=1475, v3_pass=1481, improved=6, degraded=0, uplift_pp=0.400, failcase_uplift_pp=24.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v2_pass=1433, v3_pass=1452, improved=19, degraded=0, uplift_pp=1.267, failcase_uplift_pp=28.358
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v2_pass | v3_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 500 | 484 | 490 | 6 | 0 | 1.200000 | 37.500000 | true |
| G11 | DS-003 | 500 | 472 | 483 | 11 | 0 | 2.200000 | 39.285714 | true |
| G11 | DS-006 | 500 | 494 | 494 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-002 | 500 | 494 | 494 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-003 | 500 | 489 | 491 | 2 | 0 | 0.400000 | 18.181818 | true |
| G12 | DS-006 | 500 | 492 | 496 | 4 | 0 | 0.800000 | 50.000000 | true |
| STAGE3 | DS-002 | 500 | 480 | 485 | 5 | 0 | 1.000000 | 25.000000 | true |
| STAGE3 | DS-003 | 500 | 465 | 475 | 10 | 0 | 2.000000 | 28.571429 | true |
| STAGE3 | DS-006 | 500 | 488 | 492 | 4 | 0 | 0.800000 | 33.333333 | true |
