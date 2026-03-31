# RESULT - QM Stage-2 Post-v6 Taxonomy (v1)

Date: 2026-03-04

## Scope

- Compare Stage-2 prereg raw lane vs QM Stage-1 `official-v6`
- Build post-v6 failure taxonomy over joined `2500` profiles
- Tooling only (no physics threshold/formula edits)

## Evidence

- comparison package:
  - `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v6-v1/`
- post-v6 taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v6-v1/`

## Key Metrics

- joined profiles: `2500`
- raw pass: `1750/2500`
- official-v6 projected pass: `2319/2500`
- improved `fail->pass`: `569`
- degraded `pass->fail`: `0`
- residual official fail count: `181`

Transition split:

- `pass->pass`: `1750`
- `fail->pass`: `569`
- `fail->fail`: `181`
- `pass->fail`: `0`

## Dominant Remaining Fails (official-v6)

- `G18`: `160/2500` (`6.40%`) -> dominant gate
- `G17`: `12/2500` (`0.48%`)
- `G19`: `11/2500` (`0.44%`)
- `G20`: `0/2500`

By block:

- primary: `40/600` fail (`6.67%`)
- attack: `113/1500` fail (`7.53%`)
- holdout: `28/400` fail (`7.00%`)

## Decision

Next candidate lane should target `G18` first (dominant residual error after `G17b-v4` officialization), with prereg + primary/attack/holdout and degraded=`0` as promotion rule.
