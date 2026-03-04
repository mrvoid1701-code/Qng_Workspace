# RESULT: QM Stage-1 G18-v3 Official Switch v1

Date: 2026-03-04  
Language: EN

## Candidate Promotion (v3)

All blocks passed promotion criteria with `degraded=0`.

- primary (`DS-002/003/006`, `3401..3600`):
  - `G18`: `551/600 -> 568/600`
  - `QM lane`: `513/600 -> 529/600`
- attack (`DS-002/003/006`, `3601..4100`):
  - `G18`: `1339/1500 -> 1400/1500`
  - `QM lane`: `1255/1500 -> 1316/1500`
- holdout (`DS-004/008`, `3401..3600`):
  - `G18`: `360/400 -> 372/400`
  - `QM lane`: `360/400 -> 372/400`

## Official Apply (v5)

Official mapping switched to:

- `G17`: inherited from official-v4 (`G17-v3`)
- `G18`: candidate-v3 decision status (`G18d-v3`)
- `G19/G20`: inherited unchanged

Effective tag: `qm-stage1-g18-v3-official`

## Post-switch Guard

- baseline root: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/`
- latest check decision: `PASS`

## Post-switch Taxonomy

- source: `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v3/`
- total profiles: `2500`
- fail profiles: `283` (`11.32%`)
- previous (official-v4) fail profiles: `372` (`14.88%`)
- delta: `-89` fail profiles

## Scope Guard

- no threshold changes
- no formula changes
- governance + evidence update only
