# QM Stage-1 G18b-v8 Official Switch

Date: 2026-03-05  
Effective tag: `qm-stage1-g18b-v8-official`

## Decision

QM Stage-1 official policy is switched from `official-v12` to `official-v13` with a governance-layer update on `G18b` only:

- `G18b-v8` robust trimmed-mean `n*IPR` recovery for source `G18b` fail cases
- unchanged parsed `G18b` threshold (`<5.0`) from `metric_checks_qm_info.csv`
- no core gate formulas or thresholds changed

## Promotion Evidence (PASS)

### G18b-v8

- Primary: `QM lane 600/600 -> 600/600`, degraded=`0`
- Attack: `QM lane 1496/1500 -> 1497/1500`, degraded=`0`
- Holdout: `QM lane 400/400 -> 400/400`, degraded=`0`

## Official-v13 Outcomes

- Primary: `600/600`
- Attack: `1497/1500`
- Holdout: `400/400`
- Total: `2497/2500` (`99.88%`)

Residual fail profiles: `3/2500`

- `G19`: `3` (all `DS-006`, attack)
- `G18`: `0`
- `G17`: `0`
- `G20`: `0`

## Baseline/Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v11/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v11/latest_check/`
- decision: `PASS`

## Stage-2 Projection Snapshot

Using Stage-2 raw summaries projected through `official-v13`:

- raw pass: `1750/2500`
- official pass: `2497/2500`
- improved (`fail->pass`): `747`
- degraded (`pass->fail`): `0`

## Anti Post-Hoc Guard

- candidate-only lane first (`qm-g18b-candidate-v8`)
- promotion checks on primary/attack/holdout with `degraded=0`
- threshold/formula freeze preserved
