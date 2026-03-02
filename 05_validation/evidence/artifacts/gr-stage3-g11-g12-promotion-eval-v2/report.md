# GR Stage-3 G11/G12 Candidate-v3 Consolidated Report

Date: 2026-03-02  
Protocol: `gr-stage3-g11-g12-candidate-v3`

## Decision

Overall recommendation: `PASS` (candidate-v3 satisfies prereg constraints across primary + attack + holdout).

## Block Summary (official-v2 -> candidate-v3)

| block | datasets | seeds | stage3 v2 pass | stage3 v3 pass | improved | degraded | decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| primary | DS-002, DS-003, DS-006 | 3401..3600 | 592/600 | 597/600 | 5 | 0 | PASS |
| attack_seed500 | DS-002, DS-003, DS-006 | 3601..4100 | 1433/1500 | 1452/1500 | 19 | 0 | PASS |
| attack_holdout | DS-004, DS-008 | 3401..3600 | 398/400 | 398/400 | 0 | 0 | PASS |

## Gate-Level Totals

### G11

- primary: `593 -> 597` (improved `4`, degraded `0`)
- attack_seed500: `1450 -> 1467` (improved `17`, degraded `0`)
- attack_holdout: `398 -> 398` (improved `0`, degraded `0`)

### G12

- primary: `599 -> 600` (improved `1`, degraded `0`)
- attack_seed500: `1475 -> 1481` (improved `6`, degraded `0`)
- attack_holdout: `400 -> 400` (improved `0`, degraded `0`)

## Remaining Primary Fails After Candidate-v3

Remaining Stage-3 fails on primary (`3/600`):

- `DS-002 seed 3436` (`G11 structural_fail`)
- `DS-003 seed 3491` (`G11 base_or_trim_q80_or_q75 fail`)
- `DS-006 seed 3436` (`G11 multi_peak_q80_or_q75 fail`)

## Prereg Constraint Check

- `degraded_vs_v2 = 0`: satisfied in all blocks
- per-dataset non-degradation: satisfied in all blocks
- primary net uplift (`improved_vs_v2 > 0`): satisfied
