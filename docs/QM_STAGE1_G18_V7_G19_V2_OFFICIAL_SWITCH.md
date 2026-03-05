# QM Stage-1 G18-v7 + G19-v2 Official Switch

Date: 2026-03-05  
Effective tag: `qm-stage1-g18-v7-g19-v2-official`

## Decision

QM Stage-1 official policy is switched from `official-v10` to `official-v11` using a combined governance-layer update:

- `G19-v2` high-signal slope envelope recovery for `G19d` fail-cases
- `G18-v7` multi-scale basin + expanded multi-window recovery for `G18d` fail-cases

No core gate formulas or thresholds were changed.

## Promotion Evidence (PASS)

### G19-v2

- Primary: `QM lane 591/600 -> 595/600`, degraded=`0`
- Attack: `QM lane 1479/1500 -> 1483/1500`, degraded=`0`
- Holdout: `QM lane 400/400 -> 400/400`, degraded=`0`

### G18-v7 (applied on top of G19-v2 outputs)

- Primary: `QM lane 595/600 -> 597/600`, degraded=`0`
- Attack: `QM lane 1483/1500 -> 1492/1500`, degraded=`0`
- Holdout: `QM lane 400/400 -> 400/400`, degraded=`0`

## Official-v11 Outcomes

- Primary: `597/600`
- Attack: `1492/1500`
- Holdout: `400/400`
- Total: `2489/2500` (`99.56%`)

Residual fail profiles: `11/2500`

- `G17`: `7` (dominant `G17b`)
- `G19`: `3`
- `G18`: `1` (`G18b`)
- `G20`: `0`

## Baseline/Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v9/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v9/latest_check/`
- decision: `PASS`

## Stage-2 Projection Snapshot

Using Stage-2 raw summaries projected through `official-v11`:

- raw pass: `1750/2500`
- official pass: `2489/2500`
- improved (`fail->pass`): `739`
- degraded (`pass->fail`): `0`
