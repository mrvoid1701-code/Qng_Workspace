# GR Stage-3 G11/G12 Candidate-v2 Promotion Eval

- eval_id: `gr-stage3-g11-g12-primary-v2`
- generated_utc: `2026-03-02T11:21:52.122931Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=581, v2_pass=593, improved=12, degraded=0, uplift_pp=2.000, failcase_uplift_pp=63.158
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=585, v2_pass=599, improved=14, degraded=0, uplift_pp=2.333, failcase_uplift_pp=93.333
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v1_pass=570, v2_pass=592, improved=22, degraded=0, uplift_pp=3.667, failcase_uplift_pp=73.333
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 200 | 195 | 198 | 3 | 0 | 1.500 | 60.000 | true |
| G11 | DS-003 | 200 | 188 | 197 | 9 | 0 | 4.500 | 75.000 | true |
| G11 | DS-006 | 200 | 198 | 198 | 0 | 0 | 0.000 | 0.000 | true |
| G12 | DS-002 | 200 | 195 | 199 | 4 | 0 | 2.000 | 80.000 | true |
| G12 | DS-003 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| G12 | DS-006 | 200 | 196 | 200 | 4 | 0 | 2.000 | 100.000 | true |
| STAGE3 | DS-002 | 200 | 191 | 197 | 6 | 0 | 3.000 | 66.667 | true |
| STAGE3 | DS-003 | 200 | 185 | 197 | 12 | 0 | 6.000 | 80.000 | true |
| STAGE3 | DS-006 | 200 | 194 | 198 | 4 | 0 | 2.000 | 66.667 | true |

