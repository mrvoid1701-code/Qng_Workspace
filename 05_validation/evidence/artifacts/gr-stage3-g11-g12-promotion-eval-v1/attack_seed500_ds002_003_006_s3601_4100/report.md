# GR Stage-3 G11/G12 Candidate-v2 Promotion Eval

- eval_id: `gr-stage3-g11-g12-attack-seed500-v2`
- generated_utc: `2026-03-02T12:03:45.525657Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=1426, v2_pass=1450, improved=24, degraded=0, uplift_pp=1.600, failcase_uplift_pp=32.432
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=1392, v2_pass=1475, improved=83, degraded=0, uplift_pp=5.533, failcase_uplift_pp=76.852
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v1_pass=1345, v2_pass=1433, improved=88, degraded=0, uplift_pp=5.867, failcase_uplift_pp=56.774
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 500 | 475 | 484 | 9 | 0 | 1.800 | 36.000 | true |
| G11 | DS-003 | 500 | 462 | 472 | 10 | 0 | 2.000 | 26.316 | true |
| G11 | DS-006 | 500 | 489 | 494 | 5 | 0 | 1.000 | 45.455 | true |
| G12 | DS-002 | 500 | 469 | 494 | 25 | 0 | 5.000 | 80.645 | true |
| G12 | DS-003 | 500 | 455 | 489 | 34 | 0 | 6.800 | 75.556 | true |
| G12 | DS-006 | 500 | 468 | 492 | 24 | 0 | 4.800 | 75.000 | true |
| STAGE3 | DS-002 | 500 | 453 | 480 | 27 | 0 | 5.400 | 57.447 | true |
| STAGE3 | DS-003 | 500 | 430 | 465 | 35 | 0 | 7.000 | 50.000 | true |
| STAGE3 | DS-006 | 500 | 462 | 488 | 26 | 0 | 5.200 | 68.421 | true |

