# G16b Hybrid Split Candidate (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:51:56.431033Z`
- profiles: `400`
- g16b_v1_pass: `314`
- g16b_v2_pass: `300`
- g16b_hybrid_pass: `326`
- improved_vs_v1: `12`
- degraded_vs_v1: `0`

## Pre-Registered Checks

- criteria:
  - low-signal fail count improves vs v1
  - high-signal fail count does not degrade vs v1
  - overall fail count does not degrade vs v1
- low-signal: v1_fail=20, hybrid_fail=8, pass=true
- high-signal: v1_fail=66, hybrid_fail=66, pass=true
- overall: v1_fail=86, hybrid_fail=74, pass=true
- verdict: `candidate acceptable for next promotion grid`

## Dataset Summary

| dataset | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| DS-004 | 200 | 43 | 50 | 37 |
| DS-008 | 200 | 43 | 50 | 37 |

## Regime Summary

| regime | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| low | 66 | 20 | 8 | 8 |
| high | 334 | 66 | 92 | 66 |

