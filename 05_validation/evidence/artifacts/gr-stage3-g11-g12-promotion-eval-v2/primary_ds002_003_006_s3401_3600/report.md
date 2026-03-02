# GR Stage-3 G11/G12 Candidate-v3 Promotion Eval

- eval_id: `gr-stage3-g11-g12-primary-v3`
- generated_utc: `2026-03-02T13:12:31.281573Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions (official-v2 -> candidate-v3)

- G11: decision=PASS, v2_pass=593, v3_pass=597, improved=4, degraded=0, uplift_pp=0.667, failcase_uplift_pp=57.143
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v2_pass=599, v3_pass=600, improved=1, degraded=0, uplift_pp=0.167, failcase_uplift_pp=100.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v2_pass=592, v3_pass=597, improved=5, degraded=0, uplift_pp=0.833, failcase_uplift_pp=62.500
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v2_pass | v3_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 200 | 198 | 199 | 1 | 0 | 0.500000 | 50.000000 | true |
| G11 | DS-003 | 200 | 197 | 199 | 2 | 0 | 1.000000 | 66.666667 | true |
| G11 | DS-006 | 200 | 198 | 199 | 1 | 0 | 0.500000 | 50.000000 | true |
| G12 | DS-002 | 200 | 199 | 200 | 1 | 0 | 0.500000 | 100.000000 | true |
| G12 | DS-003 | 200 | 200 | 200 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-006 | 200 | 200 | 200 | 0 | 0 | 0.000000 | 0.000000 | true |
| STAGE3 | DS-002 | 200 | 197 | 199 | 2 | 0 | 1.000000 | 66.666667 | true |
| STAGE3 | DS-003 | 200 | 197 | 199 | 2 | 0 | 1.000000 | 66.666667 | true |
| STAGE3 | DS-006 | 200 | 198 | 199 | 1 | 0 | 0.500000 | 50.000000 | true |
