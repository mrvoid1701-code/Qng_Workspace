# GR Stage-3 G11/G12 Candidate-v3 Promotion Eval

- eval_id: `gr-stage3-g11-attack-seed500-v5`
- generated_utc: `2026-03-04T09:18:06.191186Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- overall_decision: `PASS`

## Gate Decisions (official-v2 -> candidate-v3)

- G11: decision=PASS, v2_pass=1450, v3_pass=1481, improved=31, degraded=0, uplift_pp=2.067, failcase_uplift_pp=62.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v2_pass=1475, v3_pass=1475, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v2_pass=1433, v3_pass=1459, improved=26, degraded=0, uplift_pp=1.733, failcase_uplift_pp=38.806
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v2_pass | v3_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 500 | 484 | 494 | 10 | 0 | 2.000000 | 62.500000 | true |
| G11 | DS-003 | 500 | 472 | 491 | 19 | 0 | 3.800000 | 67.857143 | true |
| G11 | DS-006 | 500 | 494 | 496 | 2 | 0 | 0.400000 | 33.333333 | true |
| G12 | DS-002 | 500 | 494 | 494 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-003 | 500 | 489 | 489 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-006 | 500 | 492 | 492 | 0 | 0 | 0.000000 | 0.000000 | true |
| STAGE3 | DS-002 | 500 | 480 | 489 | 9 | 0 | 1.800000 | 45.000000 | true |
| STAGE3 | DS-003 | 500 | 465 | 481 | 16 | 0 | 3.200000 | 45.714286 | true |
| STAGE3 | DS-006 | 500 | 488 | 489 | 1 | 0 | 0.200000 | 8.333333 | true |
