# RESULT - QM Stage-1 G18-v4 Switch (v1)

Date: 2026-03-05

## Scope

- candidate lane: `G18-v4` (peak-envelope local-ds recovery, unchanged threshold band)
- promotion evaluation: primary + attack + holdout
- official mapping update: `qm-stage1-official-v7`
- baseline + guard refresh: `qm-stage1-regression-baseline-v5`

## Evidence Packages

- candidate:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v4/`
- promotion:
  - `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/`
- official:
  - `05_validation/evidence/artifacts/qm-stage1-official-v7/`
- baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v5/`

## Key Results (official-v6 -> official-v7)

- primary (`600`):
  - `G18: 568 -> 579` (`+11`, degraded `0`)
  - `QM lane: 560 -> 571` (`+11`, degraded `0`)
- attack (`1500`):
  - `G18: 1400 -> 1440` (`+40`, degraded `0`)
  - `QM lane: 1387 -> 1426` (`+39`, degraded `0`)
- holdout (`400`):
  - `G18: 372 -> 382` (`+10`, degraded `0`)
  - `QM lane: 372 -> 382` (`+10`, degraded `0`)

Promotion decisions:

- primary: `PASS`
- attack: `PASS`
- holdout: `PASS`

Regression guard:

- `qm-stage1-regression-baseline-v5/latest_check/regression_report.json`: `PASS`

## Stage-2 Projection

Raw Stage-2 prereg projected through official policies:

- `official-v6`: `2319/2500`
- `official-v7`: `2379/2500`
- delta: `+60` pass, `degraded=0`

Residual dominant failing gate after `official-v7` remains `G18` (`99/2500`).
