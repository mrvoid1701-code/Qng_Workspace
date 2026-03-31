# GR Stage-2 G11/G12 Candidate Promotion Evaluation (v1)

- eval_id: `gr-stage2-g11-g12-attack-holdout-v2`
- generated_utc: `2026-03-02T08:24:17.841744Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_holdout_ds004_008_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions

- G11: decision=PASS, v1_pass=390, v2_pass=394, improved=4, degraded=0, uplift_pp=1.000, failcase_uplift_pp=40.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v1_pass=388, v2_pass=400, improved=12, degraded=0, uplift_pp=3.000, failcase_uplift_pp=100.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE2: decision=PASS, v1_pass=380, v2_pass=394, improved=14, degraded=0, uplift_pp=3.500, failcase_uplift_pp=70.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-004 | 200 | 195 | 197 | 2 | 0 | 1.000 | 40.000 | true |
| G11 | DS-008 | 200 | 195 | 197 | 2 | 0 | 1.000 | 40.000 | true |
| G12 | DS-004 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| G12 | DS-008 | 200 | 194 | 200 | 6 | 0 | 3.000 | 100.000 | true |
| STAGE2 | DS-004 | 200 | 190 | 197 | 7 | 0 | 3.500 | 70.000 | true |
| STAGE2 | DS-008 | 200 | 190 | 197 | 7 | 0 | 3.500 | 70.000 | true |

