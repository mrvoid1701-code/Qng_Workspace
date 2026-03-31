# G16b-v2 Candidate Evaluation (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:49:02.226552Z`
- profiles: `400`
- g16b_v1_fail: `86`
- g16b_v2_fail: `100`
- g16b_v2_pass: `300`
- v1_fail_to_v2_pass: `12`
- v1_pass_to_v2_fail: `26`

## Pre-Registered Decision

- promotion target: `600/600 pass` (DS-002/003/006 x seeds 3401..3600)
- observed g16b-v2 pass: `300/600`
- conclusion: `NOT ELIGIBLE FOR PROMOTION` (candidate-only remains)

## Dataset Summary

| dataset | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| DS-004 | 200 | 43 | 50 | 6 | 13 |
| DS-008 | 200 | 43 | 50 | 6 | 13 |

## Signal-Regime Breakdown

| low_signal | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| true | 66 | 20 | 8 | 12 | 0 |
| false | 334 | 66 | 92 | 0 | 26 |

## Changed Decisions

| dataset | seed | v1 | v2 | branch | low_signal | r2_full | r2_high_signal | |pearson_hs| | |spearman_hs| |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-004 | 3412 | pass | fail | full_signal | false | 0.053403 | 0.109359 | 0.330695 | 0.259199 |
| DS-004 | 3439 | pass | fail | full_signal | false | 0.060440 | 0.119023 | 0.344997 | 0.255187 |
| DS-004 | 3445 | pass | fail | full_signal | false | 0.053507 | 0.265290 | 0.515063 | 0.484761 |
| DS-004 | 3451 | pass | fail | full_signal | false | 0.061158 | 0.225599 | 0.474973 | 0.440024 |
| DS-004 | 3462 | fail | pass | high_signal | true | 0.035544 | 0.083778 | 0.289445 | 0.527704 |
| DS-004 | 3473 | fail | pass | high_signal | true | 0.023675 | 0.082466 | 0.287169 | 0.468625 |
| DS-004 | 3474 | pass | fail | full_signal | false | 0.075186 | 0.267443 | 0.517149 | 0.395117 |
| DS-004 | 3478 | pass | fail | full_signal | false | 0.065490 | 0.227007 | 0.476453 | 0.532571 |
| DS-004 | 3488 | pass | fail | full_signal | false | 0.097287 | 0.305673 | 0.552877 | 0.530949 |
| DS-004 | 3516 | pass | fail | full_signal | false | 0.063547 | 0.294402 | 0.542588 | 0.413814 |
| DS-004 | 3522 | fail | pass | high_signal | true | 0.043317 | 0.201491 | 0.448877 | 0.416170 |
| DS-004 | 3541 | pass | fail | full_signal | false | 0.055846 | 0.147441 | 0.383980 | 0.388543 |
| DS-004 | 3552 | pass | fail | full_signal | false | 0.069758 | 0.253158 | 0.503148 | 0.368736 |
| DS-004 | 3555 | pass | fail | full_signal | false | 0.050217 | 0.236307 | 0.486115 | 0.554171 |
| DS-004 | 3563 | fail | pass | high_signal | true | 0.030512 | 0.120507 | 0.347141 | 0.401605 |
| DS-004 | 3565 | fail | pass | high_signal | true | 0.031825 | 0.140098 | 0.374297 | 0.375480 |
| DS-004 | 3573 | fail | pass | high_signal | true | 0.017509 | 0.086429 | 0.293987 | 0.272859 |
| DS-004 | 3587 | pass | fail | full_signal | false | 0.060138 | 0.247662 | 0.497656 | 0.464356 |
| DS-004 | 3596 | pass | fail | full_signal | false | 0.062045 | 0.180981 | 0.425418 | 0.315291 |
| DS-008 | 3412 | pass | fail | full_signal | false | 0.053403 | 0.109359 | 0.330695 | 0.259199 |
| DS-008 | 3439 | pass | fail | full_signal | false | 0.060440 | 0.119023 | 0.344997 | 0.255187 |
| DS-008 | 3445 | pass | fail | full_signal | false | 0.053507 | 0.265290 | 0.515063 | 0.484761 |
| DS-008 | 3451 | pass | fail | full_signal | false | 0.061158 | 0.225599 | 0.474973 | 0.440024 |
| DS-008 | 3462 | fail | pass | high_signal | true | 0.035544 | 0.083778 | 0.289445 | 0.527704 |
| DS-008 | 3473 | fail | pass | high_signal | true | 0.023675 | 0.082466 | 0.287169 | 0.468625 |
| DS-008 | 3474 | pass | fail | full_signal | false | 0.075186 | 0.267443 | 0.517149 | 0.395117 |
| DS-008 | 3478 | pass | fail | full_signal | false | 0.065490 | 0.227007 | 0.476453 | 0.532571 |
| DS-008 | 3488 | pass | fail | full_signal | false | 0.097287 | 0.305673 | 0.552877 | 0.530949 |
| DS-008 | 3516 | pass | fail | full_signal | false | 0.063547 | 0.294402 | 0.542588 | 0.413814 |
| DS-008 | 3522 | fail | pass | high_signal | true | 0.043317 | 0.201491 | 0.448877 | 0.416170 |
| DS-008 | 3541 | pass | fail | full_signal | false | 0.055846 | 0.147441 | 0.383980 | 0.388543 |
| DS-008 | 3552 | pass | fail | full_signal | false | 0.069758 | 0.253158 | 0.503148 | 0.368736 |
| DS-008 | 3555 | pass | fail | full_signal | false | 0.050217 | 0.236307 | 0.486115 | 0.554171 |
| DS-008 | 3563 | fail | pass | high_signal | true | 0.030512 | 0.120507 | 0.347141 | 0.401605 |
| DS-008 | 3565 | fail | pass | high_signal | true | 0.031825 | 0.140098 | 0.374297 | 0.375480 |
| DS-008 | 3573 | fail | pass | high_signal | true | 0.017509 | 0.086429 | 0.293987 | 0.272859 |
| DS-008 | 3587 | pass | fail | full_signal | false | 0.060138 | 0.247662 | 0.497656 | 0.464356 |
| DS-008 | 3596 | pass | fail | full_signal | false | 0.062045 | 0.180981 | 0.425418 | 0.315291 |

