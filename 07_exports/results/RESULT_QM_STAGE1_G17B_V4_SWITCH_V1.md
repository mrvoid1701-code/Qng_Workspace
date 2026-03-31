# RESULT - QM Stage-1 G17b-v4 Switch (v1)

Date: 2026-03-04

## Scope

- candidate lane: `G17b-v4` (high-signal slope recovery, no threshold changes)
- promotion evaluation: primary + attack + holdout
- official mapping update: `qm-stage1-official-v6`
- baseline + guard refresh: `qm-stage1-regression-baseline-v4`

## Evidence Packages

- candidate:
  - `05_validation/evidence/artifacts/qm-g17b-candidate-v4/`
- promotion:
  - `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/`
- official:
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/`
- baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/`

## Key Results

- primary (`600`):
  - `G17: 564 -> 596` (`+32`, degraded `0`)
  - `QM lane: 529 -> 560` (`+31`, degraded `0`)
- attack (`1500`):
  - `G17: 1416 -> 1492` (`+76`, degraded `0`)
  - `QM lane: 1316 -> 1387` (`+71`, degraded `0`)
- holdout (`400`):
  - `G17: 400 -> 400` (degraded `0`)
  - `QM lane: 372 -> 372` (degraded `0`)

Promotion decisions:

- primary: `PASS`
- attack: `PASS`
- holdout: `PASS`

Regression guard:

- `qm-stage1-regression-baseline-v4/latest_check/regression_report.json`: `PASS`

## Governance

- effective tag target: `qm-stage1-g17b-v4-official`
- switch note: `docs/QM_STAGE1_G17B_V4_OFFICIAL_SWITCH.md`

## Runtime Note

Requested tracking note: full package recorded as approximately `5h` process window.
