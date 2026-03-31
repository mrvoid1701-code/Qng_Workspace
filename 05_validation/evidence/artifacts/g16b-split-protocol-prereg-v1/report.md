# G16b Split Protocol Candidate (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:37:42.601004Z`
- profiles: `600`
- g16b_v1_pass: `473`
- g16b_v2_pass: `487`
- g16b_split_pass: `500`

## Pre-Registered Split Checks

- criteria:
  - low-signal fail count improves vs v1
  - high-signal fail count does not degrade vs v1
  - overall fail count does not degrade vs v1
- low-signal: v1_fail=62, split_fail=20, pass=true
- high-signal: v1_fail=65, split_fail=80, pass=false
- overall: v1_fail=127, split_fail=100, pass=true
- verdict: `candidate NOT acceptable yet`

## Dataset Summary

| dataset | n | v1_fail | v2_fail | split_fail |
| --- | --- | --- | --- | --- |
| DS-002 | 200 | 42 | 40 | 36 |
| DS-003 | 200 | 41 | 41 | 51 |
| DS-006 | 200 | 44 | 32 | 13 |

## Regime Summary

| regime | n | v1_fail | v2_fail | split_fail |
| --- | --- | --- | --- | --- |
| low | 311 | 62 | 53 | 20 |
| high | 289 | 65 | 60 | 80 |

## Decision Changes vs v1 (first 40)

| dataset | seed | regime | v1 | split | signal_index | abs_pearson_full | abs_cosine_full | r2_origin_full |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 3418 | low | fail | pass | 0.022771 | 0.142235 | 0.143046 | 0.020034 |
| DS-002 | 3427 | low | fail | pass | 0.023198 | 0.185736 | 0.182813 | 0.033033 |
| DS-002 | 3430 | low | fail | pass | 0.022138 | 0.193885 | 0.188320 | 0.034584 |
| DS-002 | 3470 | high | pass | fail | 0.024974 | 0.230018 | 0.220018 | 0.045718 |
| DS-002 | 3471 | low | fail | pass | 0.023327 | 0.170597 | 0.165560 | 0.027177 |
| DS-002 | 3479 | low | fail | pass | 0.020198 | 0.144857 | 0.133496 | 0.017044 |
| DS-002 | 3480 | high | pass | fail | 0.025052 | 0.246024 | 0.240065 | 0.047329 |
| DS-002 | 3482 | high | pass | fail | 0.026056 | 0.294492 | 0.252163 | 0.028994 |
| DS-002 | 3486 | low | pass | fail | 0.019471 | 0.247528 | 0.240575 | 0.057663 |
| DS-002 | 3489 | low | fail | pass | 0.023820 | 0.150172 | 0.152713 | 0.016894 |
| DS-002 | 3495 | high | pass | fail | 0.029445 | 0.242101 | 0.259198 | 0.046805 |
| DS-002 | 3540 | low | fail | pass | 0.022575 | 0.213549 | 0.220615 | 0.045147 |
| DS-002 | 3541 | high | pass | fail | 0.024844 | 0.225014 | 0.213002 | 0.044491 |
| DS-002 | 3554 | low | fail | pass | 0.022698 | 0.171252 | 0.194590 | 0.024788 |
| DS-002 | 3568 | low | fail | pass | 0.023457 | 0.184038 | 0.174266 | 0.029970 |
| DS-002 | 3573 | low | fail | pass | 0.021909 | 0.192975 | 0.189830 | 0.034554 |
| DS-002 | 3584 | low | fail | pass | 0.020400 | 0.221257 | 0.221180 | 0.048217 |
| DS-002 | 3600 | low | fail | pass | 0.021902 | 0.174588 | 0.174736 | 0.029732 |
| DS-003 | 3415 | low | pass | fail | 0.023452 | 0.242061 | 0.222799 | 0.047898 |
| DS-003 | 3417 | high | pass | fail | 0.024027 | 0.249565 | 0.229566 | 0.045786 |
| DS-003 | 3419 | low | pass | fail | 0.022448 | 0.301732 | 0.279307 | 0.077676 |
| DS-003 | 3454 | high | pass | fail | 0.025767 | 0.227107 | 0.202925 | 0.033357 |
| DS-003 | 3456 | high | pass | fail | 0.034086 | 0.226279 | 0.221287 | 0.048690 |
| DS-003 | 3467 | low | fail | pass | 0.023421 | 0.223069 | 0.245308 | 0.047842 |
| DS-003 | 3514 | high | pass | fail | 0.025391 | 0.249140 | 0.248279 | 0.048460 |
| DS-003 | 3525 | low | fail | pass | 0.023057 | 0.073345 | 0.074154 | 0.005359 |
| DS-003 | 3526 | high | pass | fail | 0.025719 | 0.255465 | 0.232978 | 0.048715 |
| DS-003 | 3528 | high | pass | fail | 0.025321 | 0.241497 | 0.211930 | 0.036796 |
| DS-003 | 3541 | high | pass | fail | 0.031136 | 0.284591 | 0.229146 | 0.040428 |
| DS-003 | 3552 | high | pass | fail | 0.026900 | 0.261788 | 0.227783 | 0.049560 |
| DS-003 | 3574 | high | pass | fail | 0.024004 | 0.246818 | 0.191508 | 0.000000 |
| DS-003 | 3584 | low | pass | fail | 0.022293 | 0.251799 | 0.242007 | 0.058445 |
| DS-006 | 3411 | low | fail | pass | 0.021640 | 0.213167 | 0.215402 | 0.043103 |
| DS-006 | 3418 | low | fail | pass | 0.019663 | 0.209464 | 0.207099 | 0.034165 |
| DS-006 | 3424 | low | fail | pass | 0.022615 | 0.223023 | 0.220122 | 0.043328 |
| DS-006 | 3426 | low | fail | pass | 0.020631 | 0.221577 | 0.213535 | 0.043468 |
| DS-006 | 3434 | low | fail | pass | 0.020421 | 0.205066 | 0.207903 | 0.040469 |
| DS-006 | 3439 | low | fail | pass | 0.021156 | 0.194679 | 0.187743 | 0.032945 |
| DS-006 | 3444 | low | fail | pass | 0.021597 | 0.159251 | 0.159279 | 0.025340 |
| DS-006 | 3451 | low | fail | pass | 0.021514 | 0.200669 | 0.197317 | 0.037365 |

