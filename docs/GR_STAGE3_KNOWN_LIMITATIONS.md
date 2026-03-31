# GR Stage-3 Known Limitations (Official v5)

Date: 2026-03-04  
Effective tag: `gr-stage3-g11-v5-official`

## Scope

This note captures current limitations after the Stage-3 v5 governance switch.

## Current Official Readout

- Source package: `05_validation/evidence/artifacts/gr-stage3-official-v5/`
- Profiles (primary): `600`
- Official Stage-3 pass (primary): `600/600`
- Remaining primary fails: `0/600`

## Current Limitation Area

Primary closure is complete, but non-primary tails still exist:

- attack block (`DS-002/003/006`, seeds `3601..4100`): `1459/1500`
- holdout block (`DS-004/008`, seeds `3401..3600`): `400/400`

Interpretation:

- no remaining fail class in primary Stage-3 official package;
- tail sensitivity is now concentrated in attack distribution, not in primary closure.

## Governance Notes

- No gate formula changes and no threshold edits were applied.
- Official v5 switch is governance-layer mapping over frozen runs.
- Regression guard for official-v5 baseline is `PASS`:
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v2/latest_check/regression_report.json`
