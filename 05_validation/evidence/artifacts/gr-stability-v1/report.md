# GR Stability Report (v1)

- generated_utc: `2026-03-01T22:49:01.323936Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`
- freeze_tag: `gr-ppn-g15b-v2-official`

## Dataset Stats

| dataset | n | all_pass | g13_pass | g14_pass | g15_pass | g16_pass | g15b_v2_pass | g13b_p95 | g14b_p95 | g13c_p05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | 60 | 0.6167 | 1.0000 | 1.0000 | 0.8000 | 0.8500 | 1.0000 | 0.004706 | 0.002745 | 0.123994 |
| DS-002 | 20 | 0.8000 | 1.0000 | 1.0000 | 0.9500 | 0.8500 | 1.0000 | 0.004611 | 0.002132 | 0.146082 |
| DS-003 | 20 | 0.1500 | 1.0000 | 1.0000 | 0.4500 | 0.8000 | 1.0000 | 0.005016 | 0.003407 | 0.167957 |
| DS-006 | 20 | 0.9000 | 1.0000 | 1.0000 | 1.0000 | 0.9000 | 1.0000 | 0.004653 | 0.001585 | 0.122975 |

## Worst-Case Rows

| metric | rank | dataset | seed | phi | value | all_pass |
| --- | --- | --- | --- | --- | --- | --- |
| g13b_e_cov_drift | 1 | DS-002 | 3419 | 0.08 | 0.005248 | pass |
| g13b_e_cov_drift | 2 | DS-003 | 3405 | 0.08 | 0.005204 | fail |
| g13b_e_cov_drift | 3 | DS-003 | 3419 | 0.08 | 0.005006 | pass |
| g13b_e_cov_drift | 4 | DS-006 | 3404 | 0.08 | 0.004690 | pass |
| g13b_e_cov_drift | 5 | DS-006 | 3408 | 0.08 | 0.004651 | pass |
| g13b_e_cov_drift | 6 | DS-002 | 3420 | 0.08 | 0.004577 | fail |
| g13b_e_cov_drift | 7 | DS-002 | 3405 | 0.08 | 0.004436 | pass |
| g13b_e_cov_drift | 8 | DS-002 | 3403 | 0.08 | 0.004428 | pass |
| g13b_e_cov_drift | 9 | DS-002 | 3413 | 0.08 | 0.004394 | pass |
| g13b_e_cov_drift | 10 | DS-003 | 3401 | 0.08 | 0.004385 | fail |
| g14b_e_cov_drift | 1 | DS-003 | 3402 | 0.08 | 0.003625 | fail |
| g14b_e_cov_drift | 2 | DS-003 | 3415 | 0.08 | 0.003396 | pass |
| g14b_e_cov_drift | 3 | DS-003 | 3409 | 0.08 | 0.003163 | fail |
| g14b_e_cov_drift | 4 | DS-002 | 3404 | 0.08 | 0.002723 | pass |
| g14b_e_cov_drift | 5 | DS-003 | 3403 | 0.08 | 0.002431 | fail |
| g14b_e_cov_drift | 6 | DS-003 | 3417 | 0.08 | 0.002177 | fail |
| g14b_e_cov_drift | 7 | DS-002 | 3407 | 0.08 | 0.002101 | pass |
| g14b_e_cov_drift | 8 | DS-003 | 3401 | 0.08 | 0.001927 | fail |
| g14b_e_cov_drift | 9 | DS-003 | 3416 | 0.08 | 0.001847 | fail |
| g14b_e_cov_drift | 10 | DS-002 | 3402 | 0.08 | 0.001799 | pass |
| g13c_speed_reduction | 1 | DS-006 | 3418 | 0.08 | 0.120298 | fail |
| g13c_speed_reduction | 2 | DS-006 | 3415 | 0.08 | 0.123116 | pass |
| g13c_speed_reduction | 3 | DS-006 | 3402 | 0.08 | 0.123777 | pass |
| g13c_speed_reduction | 4 | DS-006 | 3413 | 0.08 | 0.124005 | pass |
| g13c_speed_reduction | 5 | DS-006 | 3407 | 0.08 | 0.124642 | pass |
| g13c_speed_reduction | 6 | DS-006 | 3401 | 0.08 | 0.125288 | pass |
| g13c_speed_reduction | 7 | DS-006 | 3404 | 0.08 | 0.125344 | pass |
| g13c_speed_reduction | 8 | DS-006 | 3410 | 0.08 | 0.126336 | pass |
| g13c_speed_reduction | 9 | DS-006 | 3414 | 0.08 | 0.126876 | pass |
| g13c_speed_reduction | 10 | DS-006 | 3406 | 0.08 | 0.127435 | pass |

