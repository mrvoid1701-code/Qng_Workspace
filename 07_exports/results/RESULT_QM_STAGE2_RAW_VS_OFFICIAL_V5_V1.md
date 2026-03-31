# RESULT: QM Stage-2 Raw vs Official-v5 Comparison v1

Date: 2026-03-04  
Language: EN

## Scope

Comparison between:

- raw Stage-2 prereg summaries:
  - `qm-stage2-prereg-v1/*/qm_lane/summary.csv`
- official governance summaries:
  - `qm-stage1-official-v5/*/summary.csv`

Profile grid matched exactly:

- primary `DS-002/003/006` seeds `3401..3600`
- attack `DS-002/003/006` seeds `3601..4100`
- holdout `DS-004/008` seeds `3401..3600`

## Headline

- joined profiles: `2500`
- missing/extra profiles: `0/0`
- raw pass: `1750/2500` (`70.00%`)
- official-v5 pass: `2217/2500` (`88.68%`)
- improved (`fail->pass`): `467`
- degraded (`pass->fail`): `0`

## Transition counts

- `pass->pass`: `1750`
- `fail->pass`: `467`
- `fail->fail`: `283`

## Gate deltas

- `g17_status` changed on `493` profiles
- `g18_status` changed on `90` profiles

Interpretation: most Stage-2 HOLD pressure in raw summaries was policy-layer recoverable via frozen official mappings, with zero degradation.

## Artifacts

- `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1/profile_deltas.csv`
- `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1/summary_transition.csv`
- `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1/profile_mismatch_keys.csv`
- `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1/report.md`
