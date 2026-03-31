# G16b Hybrid Split Candidate (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:51:56.447627Z`
- profiles: `1500`
- g16b_v1_pass: `1156`
- g16b_v2_pass: `1207`
- g16b_hybrid_pass: `1266`
- improved_vs_v1: `110`
- degraded_vs_v1: `0`

## Pre-Registered Checks

- criteria:
  - low-signal fail count improves vs v1
  - high-signal fail count does not degrade vs v1
  - overall fail count does not degrade vs v1
- low-signal: v1_fail=145, hybrid_fail=35, pass=true
- high-signal: v1_fail=199, hybrid_fail=199, pass=true
- overall: v1_fail=344, hybrid_fail=234, pass=true
- verdict: `candidate acceptable for next promotion grid`

## Dataset Summary

| dataset | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| DS-002 | 500 | 102 | 106 | 78 |
| DS-003 | 500 | 125 | 128 | 114 |
| DS-006 | 500 | 117 | 59 | 42 |

## Regime Summary

| regime | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| low | 538 | 145 | 35 | 35 |
| high | 962 | 199 | 258 | 199 |

