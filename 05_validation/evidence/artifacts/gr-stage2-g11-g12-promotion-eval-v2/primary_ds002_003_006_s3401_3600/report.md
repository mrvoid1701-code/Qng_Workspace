# GR Stage-2 G11/G12 Candidate Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-g12-primary-v2`
- generated_utc: `2026-03-02T08:23:11.281570Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=581, v2_pass=587, improved=6, degraded=0, uplift_pp=1.000, failcase_uplift_pp=31.579
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=585, v2_pass=600, improved=15, degraded=0, uplift_pp=2.500, failcase_uplift_pp=100.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE2: decision=PASS, v1_pass=570, v2_pass=587, improved=17, degraded=0, uplift_pp=2.833, failcase_uplift_pp=56.667
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-002 | 200 | 195 | 197 | 2 | 0 | 1.000 | 40.000 | true |
| G11 | DS-003 | 200 | 188 | 192 | 4 | 0 | 2.000 | 33.333 | true |
| G11 | DS-006 | 200 | 198 | 198 | 0 | 0 | 0.000 | 0.000 | true |
| G12 | DS-002 | 200 | 195 | 200 | 5 | 0 | 2.500 | 100.000 | true |
| G12 | DS-003 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| G12 | DS-006 | 200 | 196 | 200 | 4 | 0 | 2.000 | 100.000 | true |
| STAGE2 | DS-002 | 200 | 191 | 197 | 6 | 0 | 3.000 | 66.667 | true |
| STAGE2 | DS-003 | 200 | 185 | 192 | 7 | 0 | 3.500 | 46.667 | true |
| STAGE2 | DS-006 | 200 | 194 | 198 | 4 | 0 | 2.000 | 66.667 | true |

