# GR Stage-3 G11/G12 Candidate-v3 Promotion Eval

- eval_id: `gr-stage3-g11-g12-attack-holdout-v3`
- generated_utc: `2026-03-02T13:13:34.467061Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv`
- overall_decision: `PASS`

## Gate Decisions (official-v2 -> candidate-v3)

- G11: decision=PASS, v2_pass=398, v3_pass=398, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- G12: decision=PASS, v2_pass=400, v3_pass=400, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true
- STAGE3: decision=PASS, v2_pass=398, v3_pass=398, improved=0, degraded=0, uplift_pp=0.000, failcase_uplift_pp=0.000
  checks: zero_degraded=true, net_uplift_failcases=true, per_dataset_nondegrade=true

## Dataset Summary

| gate | dataset | n | v2_pass | v3_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G11 | DS-004 | 200 | 199 | 199 | 0 | 0 | 0.000000 | 0.000000 | true |
| G11 | DS-008 | 200 | 199 | 199 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-004 | 200 | 200 | 200 | 0 | 0 | 0.000000 | 0.000000 | true |
| G12 | DS-008 | 200 | 200 | 200 | 0 | 0 | 0.000000 | 0.000000 | true |
| STAGE3 | DS-004 | 200 | 199 | 199 | 0 | 0 | 0.000000 | 0.000000 | true |
| STAGE3 | DS-008 | 200 | 199 | 199 | 0 | 0 | 0.000000 | 0.000000 | true |
