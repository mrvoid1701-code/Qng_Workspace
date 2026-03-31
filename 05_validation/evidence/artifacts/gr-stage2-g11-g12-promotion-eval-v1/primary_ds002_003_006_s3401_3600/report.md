# GR Stage-2 G11/G12 Candidate Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-g12-primary-v1`
- generated_utc: `2026-03-02T01:18:43.172563Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600/summary.csv`
- overall_decision: `FAIL`

## Gate Decisions

- G11: decision=FAIL, v1_pass=581, v2_pass=581, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=false, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=585, v2_pass=600, improved=15, degraded=0, uplift_pp=2.500, failcase_uplift_pp=100.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE2: decision=PASS, v1_pass=570, v2_pass=581, improved=11, degraded=0, uplift_pp=1.833, failcase_uplift_pp=36.667
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 200 | 195 | 195 | 0 | 0 | 0.000 | 0.000 | true |
| G11 | DS-003 | 200 | 188 | 188 | 0 | 0 | 0.000 | 0.000 | true |
| G11 | DS-006 | 200 | 198 | 198 | 0 | 0 | 0.000 | 0.000 | true |
| G12 | DS-002 | 200 | 195 | 200 | 5 | 0 | 2.500 | 100.000 | true |
| G12 | DS-003 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| G12 | DS-006 | 200 | 196 | 200 | 4 | 0 | 2.000 | 100.000 | true |
| STAGE2 | DS-002 | 200 | 191 | 195 | 4 | 0 | 2.000 | 44.444 | true |
| STAGE2 | DS-003 | 200 | 185 | 188 | 3 | 0 | 1.500 | 20.000 | true |
| STAGE2 | DS-006 | 200 | 194 | 198 | 4 | 0 | 2.000 | 66.667 | true |

