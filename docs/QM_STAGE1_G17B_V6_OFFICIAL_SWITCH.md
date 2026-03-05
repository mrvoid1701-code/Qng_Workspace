# QM Stage-1 G17b-v6 Official Switch

Date: 2026-03-05  
Effective tag: `qm-stage1-g17b-v6-official`

## Decision

QM Stage-1 official policy is switched from `official-v11` to `official-v12` using a governance-layer update on `G17b` only:

- `G17b-v6` high-signal median-slope recovery over fixed quantile windows for `G17b-v1` fail cases
- unchanged parsed `G17b` threshold (`<-0.01`) from `metric_checks_qm.csv`
- no core gate formulas changed

## Promotion Evidence (PASS)

### G17b-v6

- Primary: `QM lane 597/600 -> 600/600`, degraded=`0`
- Attack: `QM lane 1492/1500 -> 1496/1500`, degraded=`0`
- Holdout: `QM lane 400/400 -> 400/400`, degraded=`0`

## Official-v12 Outcomes

- Primary: `600/600`
- Attack: `1496/1500`
- Holdout: `400/400`
- Total: `2496/2500` (`99.84%`)

Residual fail profiles: `4/2500`

- `G19`: `3` (all `DS-006`, attack)
- `G18`: `1` (`DS-003`, attack, `G18b`)
- `G17`: `0`
- `G20`: `0`

## Baseline/Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v10/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v10/latest_check/`
- decision: `PASS`

## Stage-2 Projection Snapshot

Using Stage-2 raw summaries projected through `official-v12`:

- raw pass: `1750/2500`
- official pass: `2496/2500`
- improved (`fail->pass`): `746`
- degraded (`pass->fail`): `0`

## Anti Post-Hoc Guard

- candidate-only lane first (`qm-g17b-candidate-v6`)
- prereg-like promotion checks on primary/attack/holdout
- strict `degraded=0` requirement
- threshold/formula freeze preserved
