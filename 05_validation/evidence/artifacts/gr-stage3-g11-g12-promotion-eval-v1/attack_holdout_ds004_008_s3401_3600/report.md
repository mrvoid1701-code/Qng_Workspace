# GR Stage-3 G11/G12 Candidate-v2 Promotion Eval

- eval_id: `gr-stage3-g11-g12-attack-holdout-v2`
- generated_utc: `2026-03-02T12:14:24.820271Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=390, v2_pass=398, improved=8, degraded=0, uplift_pp=2.000, failcase_uplift_pp=80.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=388, v2_pass=400, improved=12, degraded=0, uplift_pp=3.000, failcase_uplift_pp=100.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v1_pass=380, v2_pass=398, improved=18, degraded=0, uplift_pp=4.500, failcase_uplift_pp=90.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-004 | 200 | 195 | 199 | 4 | 0 | 2.000 | 80.000 | true |
| G11 | DS-008 | 200 | 195 | 199 | 4 | 0 | 2.000 | 80.000 | true |
| G12 | DS-004 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| G12 | DS-008 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| STAGE3 | DS-004 | 200 | 190 | 199 | 9 | 0 | 4.500 | 90.000 | true |
| STAGE3 | DS-008 | 200 | 190 | 199 | 9 | 0 | 4.500 | 90.000 | true |

