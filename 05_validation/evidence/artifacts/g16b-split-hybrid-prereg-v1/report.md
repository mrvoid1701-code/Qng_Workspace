# G16b Hybrid Split Candidate (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:40:56.885607Z`
- profiles: `600`
- g16b_v1_pass: `473`
- g16b_v2_pass: `487`
- g16b_hybrid_pass: `516`
- improved_vs_v1: `43`
- degraded_vs_v1: `0`

## Pre-Registered Checks

- criteria:
  - low-signal fail count improves vs v1
  - high-signal fail count does not degrade vs v1
  - overall fail count does not degrade vs v1
- low-signal: v1_fail=60, hybrid_fail=17, pass=true
- high-signal: v1_fail=67, hybrid_fail=67, pass=true
- overall: v1_fail=127, hybrid_fail=84, pass=true
- verdict: `candidate acceptable for next promotion grid`

## Dataset Summary

| dataset | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| DS-002 | 200 | 42 | 40 | 28 |
| DS-003 | 200 | 41 | 41 | 38 |
| DS-006 | 200 | 44 | 32 | 18 |

## Regime Summary

| regime | n | v1_fail | v2_fail | hybrid_fail |
| --- | --- | --- | --- | --- |
| low | 210 | 60 | 17 | 17 |
| high | 390 | 67 | 96 | 67 |

