# GR Stage-3 G11/G12 Candidate-v2 Consolidated Report

Date: 2026-03-02
Protocol: `gr-stage3-g11-g12-candidate-v2`

## Decision

Overall recommendation: `PASS` (candidate satisfies prereg constraints across primary + attack + holdout).

## Block Summary

| block | datasets | seeds | stage3 v1 pass | stage3 v2 pass | improved | degraded | decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| primary | DS-002, DS-003, DS-006 | 3401..3600 | 570/600 | 592/600 | 22 | 0 | PASS |
| attack_seed500 | DS-002, DS-003, DS-006 | 3601..4100 | 1345/1500 | 1433/1500 | 88 | 0 | PASS |
| attack_holdout | DS-004, DS-008 | 3401..3600 | 380/400 | 398/400 | 18 | 0 | PASS |

## Gate-Level Totals

### G11

- primary: `581 -> 593` (improved `12`, degraded `0`)
- attack_seed500: `1426 -> 1450` (improved `24`, degraded `0`)
- attack_holdout: `390 -> 398` (improved `8`, degraded `0`)

### G12

- primary: `585 -> 599` (improved `14`, degraded `0`)
- attack_seed500: `1392 -> 1475` (improved `83`, degraded `0`)
- attack_holdout: `388 -> 400` (improved `12`, degraded `0`)

## Prereg Constraint Check

- `degraded_vs_v1 = 0`: satisfied in all blocks
- per-dataset non-degradation: satisfied in all blocks
- primary net uplift (`improved_vs_v1 > 0`): satisfied

## Source Reports

- `primary_ds002_003_006_s3401_3600/report.json`
- `attack_seed500_ds002_003_006_s3601_4100/report.json`
- `attack_holdout_ds004_008_s3401_3600/report.json`
