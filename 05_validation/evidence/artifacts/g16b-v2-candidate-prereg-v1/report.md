# G16b-v2 Candidate Evaluation (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:29:09.429787Z`
- profiles: `600`
- g16b_v1_fail: `127`
- g16b_v2_fail: `113`
- g16b_v2_pass: `487`
- v1_fail_to_v2_pass: `43`
- v1_pass_to_v2_fail: `29`

## Pre-Registered Decision

- promotion target: `600/600 pass` (DS-002/003/006 x seeds 3401..3600)
- observed g16b-v2 pass: `487/600`
- conclusion: `NOT ELIGIBLE FOR PROMOTION` (candidate-only remains)

## Dataset Summary

| dataset | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| DS-002 | 200 | 42 | 40 | 14 | 12 |
| DS-003 | 200 | 41 | 41 | 3 | 3 |
| DS-006 | 200 | 44 | 32 | 26 | 14 |

## Signal-Regime Breakdown

| low_signal | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| true | 210 | 60 | 17 | 43 | 0 |
| false | 390 | 67 | 96 | 0 | 29 |

## Changed Decisions

| dataset | seed | v1 | v2 | branch | low_signal | r2_full | r2_high_signal | |pearson_hs| | |spearman_hs| |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 3415 | pass | fail | full_signal | false | 0.079641 | 0.330973 | 0.575303 | 0.472249 |
| DS-002 | 3418 | fail | pass | high_signal | true | 0.020231 | 0.157561 | 0.396939 | 0.690157 |
| DS-002 | 3420 | fail | pass | high_signal | true | 0.022709 | 0.093429 | 0.305661 | 0.583185 |
| DS-002 | 3424 | pass | fail | full_signal | false | 0.074203 | 0.292252 | 0.540604 | 0.519139 |
| DS-002 | 3427 | fail | pass | high_signal | true | 0.034498 | 0.167643 | 0.409443 | 0.372249 |
| DS-002 | 3429 | fail | pass | high_signal | true | 0.033411 | 0.068531 | 0.261784 | 0.253247 |
| DS-002 | 3438 | pass | fail | full_signal | false | 0.054252 | 0.126535 | 0.355717 | 0.325906 |
| DS-002 | 3445 | fail | pass | high_signal | true | 0.046012 | 0.223054 | 0.472286 | 0.459467 |
| DS-002 | 3458 | pass | fail | full_signal | false | 0.089106 | 0.344071 | 0.586576 | 0.579289 |
| DS-002 | 3464 | fail | pass | high_signal | true | 0.045084 | 0.212812 | 0.461316 | 0.639508 |
| DS-002 | 3472 | pass | fail | full_signal | false | 0.070024 | 0.369750 | 0.608071 | 0.565662 |
| DS-002 | 3489 | fail | pass | high_signal | true | 0.022552 | 0.096153 | 0.310085 | 0.468079 |
| DS-002 | 3492 | pass | fail | full_signal | false | 0.058420 | 0.214075 | 0.462683 | 0.273206 |
| DS-002 | 3501 | pass | fail | full_signal | false | 0.053774 | 0.165834 | 0.407227 | 0.266507 |
| DS-002 | 3512 | fail | pass | high_signal | true | 0.022775 | 0.073760 | 0.271589 | 0.279152 |
| DS-002 | 3514 | fail | pass | high_signal | true | 0.030473 | 0.125403 | 0.354123 | 0.358852 |
| DS-002 | 3516 | pass | fail | full_signal | false | 0.073338 | 0.321665 | 0.567155 | 0.384484 |
| DS-002 | 3541 | pass | fail | full_signal | false | 0.050631 | 0.210197 | 0.458473 | 0.437662 |
| DS-002 | 3547 | fail | pass | high_signal | true | 0.043444 | 0.095756 | 0.309444 | 0.484621 |
| DS-002 | 3551 | fail | pass | high_signal | true | 0.042950 | 0.141985 | 0.376809 | 0.650718 |
| DS-002 | 3559 | pass | fail | full_signal | false | 0.066685 | 0.302983 | 0.550439 | 0.469925 |
| DS-002 | 3563 | fail | pass | high_signal | true | 0.035467 | 0.121848 | 0.349068 | 0.517020 |
| DS-002 | 3565 | pass | fail | full_signal | false | 0.052174 | 0.385627 | 0.620989 | 0.485167 |
| DS-002 | 3570 | fail | pass | high_signal | true | 0.047978 | 0.248811 | 0.498809 | 0.506699 |
| DS-002 | 3573 | fail | pass | high_signal | true | 0.037239 | 0.223703 | 0.472972 | 0.535543 |
| DS-002 | 3598 | pass | fail | full_signal | false | 0.055451 | 0.194912 | 0.441488 | 0.387628 |
| DS-003 | 3405 | fail | pass | high_signal | true | 0.048156 | 0.118488 | 0.344220 | 0.438124 |
| DS-003 | 3445 | fail | pass | high_signal | true | 0.047297 | 0.193705 | 0.440120 | 0.575554 |
| DS-003 | 3472 | pass | fail | full_signal | false | 0.070335 | 0.233856 | 0.483587 | 0.444855 |
| DS-003 | 3525 | fail | pass | high_signal | true | 0.005380 | 0.057159 | 0.239079 | 0.337603 |
| DS-003 | 3541 | pass | fail | full_signal | false | 0.080992 | 0.155891 | 0.394830 | 0.429114 |
| DS-003 | 3598 | pass | fail | full_signal | false | 0.077753 | 0.301741 | 0.549310 | 0.495766 |
| DS-006 | 3404 | pass | fail | full_signal | false | 0.092237 | 0.384066 | 0.619730 | 0.579121 |
| DS-006 | 3411 | fail | pass | high_signal | true | 0.045440 | 0.262328 | 0.512180 | 0.497527 |
| DS-006 | 3412 | pass | fail | full_signal | false | 0.071959 | 0.280359 | 0.529489 | 0.577060 |
| DS-006 | 3418 | fail | pass | high_signal | true | 0.043875 | 0.260548 | 0.510439 | 0.565064 |
| DS-006 | 3424 | fail | pass | high_signal | true | 0.049739 | 0.256040 | 0.506004 | 0.589469 |
| DS-006 | 3434 | fail | pass | high_signal | true | 0.042052 | 0.327580 | 0.572346 | 0.577152 |
| DS-006 | 3437 | pass | fail | full_signal | false | 0.050136 | 0.300571 | 0.548243 | 0.504441 |
| DS-006 | 3438 | pass | fail | full_signal | false | 0.086925 | 0.338541 | 0.581843 | 0.566621 |
| DS-006 | 3444 | fail | pass | high_signal | true | 0.025361 | 0.079016 | 0.281097 | 0.447253 |
| DS-006 | 3451 | fail | pass | high_signal | true | 0.040268 | 0.215067 | 0.463753 | 0.475000 |
| DS-006 | 3455 | pass | fail | full_signal | false | 0.124690 | 0.503206 | 0.709370 | 0.675778 |
| DS-006 | 3456 | pass | fail | full_signal | false | 0.050239 | 0.349499 | 0.591185 | 0.620513 |
| DS-006 | 3457 | pass | fail | full_signal | false | 0.075497 | 0.296373 | 0.544401 | 0.564011 |
| DS-006 | 3473 | fail | pass | high_signal | true | 0.024142 | 0.118407 | 0.344103 | 0.609295 |
| DS-006 | 3479 | fail | pass | high_signal | true | 0.041029 | 0.336337 | 0.579945 | 0.623901 |
| DS-006 | 3481 | fail | pass | high_signal | true | 0.025217 | 0.143748 | 0.379142 | 0.338004 |
| DS-006 | 3488 | fail | pass | high_signal | true | 0.032122 | 0.130377 | 0.361077 | 0.508837 |
| DS-006 | 3489 | fail | pass | high_signal | true | 0.038095 | 0.153675 | 0.392014 | 0.450733 |
| DS-006 | 3496 | pass | fail | full_signal | false | 0.053686 | 0.198443 | 0.445469 | 0.427244 |
| DS-006 | 3500 | pass | fail | full_signal | false | 0.056261 | 0.151058 | 0.388662 | 0.451145 |
| DS-006 | 3505 | pass | fail | full_signal | false | 0.057800 | 0.396645 | 0.629797 | 0.624084 |
| DS-006 | 3506 | fail | pass | high_signal | true | 0.044301 | 0.105313 | 0.324519 | 0.306410 |
| DS-006 | 3507 | pass | fail | full_signal | false | 0.094146 | 0.337612 | 0.581044 | 0.580174 |
| DS-006 | 3509 | fail | pass | high_signal | true | 0.041901 | 0.253885 | 0.503870 | 0.551465 |
| DS-006 | 3512 | fail | pass | high_signal | true | 0.044159 | 0.167379 | 0.409120 | 0.457354 |
| DS-006 | 3532 | fail | pass | high_signal | true | 0.027045 | 0.050723 | 0.225218 | 0.380952 |
| DS-006 | 3534 | fail | pass | high_signal | true | 0.048342 | 0.252477 | 0.502471 | 0.463690 |
| DS-006 | 3537 | fail | pass | high_signal | true | 0.031181 | 0.138132 | 0.371661 | 0.413278 |
| DS-006 | 3543 | fail | pass | high_signal | true | 0.020564 | 0.153433 | 0.391705 | 0.421662 |
| DS-006 | 3550 | pass | fail | full_signal | false | 0.072188 | 0.334093 | 0.578008 | 0.534982 |
| DS-006 | 3553 | fail | pass | high_signal | true | 0.041783 | 0.201908 | 0.449342 | 0.432738 |
| DS-006 | 3558 | fail | pass | high_signal | true | 0.027511 | 0.112008 | 0.334676 | 0.360440 |
| DS-006 | 3563 | fail | pass | high_signal | true | 0.048838 | 0.226565 | 0.475989 | 0.652335 |
| DS-006 | 3565 | fail | pass | high_signal | true | 0.028863 | 0.151711 | 0.389501 | 0.382692 |
| DS-006 | 3566 | pass | fail | full_signal | false | 0.064816 | 0.296762 | 0.544759 | 0.570055 |
| DS-006 | 3568 | fail | pass | high_signal | true | 0.025022 | 0.140870 | 0.375327 | 0.428480 |
| DS-006 | 3571 | fail | pass | high_signal | true | 0.032844 | 0.234319 | 0.484065 | 0.457601 |
| DS-006 | 3576 | fail | pass | high_signal | true | 0.049756 | 0.301620 | 0.549199 | 0.587683 |
| DS-006 | 3581 | fail | pass | high_signal | true | 0.048983 | 0.238770 | 0.488641 | 0.468132 |
| DS-006 | 3598 | pass | fail | full_signal | false | 0.055010 | 0.292221 | 0.540575 | 0.482326 |

