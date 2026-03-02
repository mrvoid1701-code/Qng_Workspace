# GR Stage-3 Known Limitations (Official v3)

Date: 2026-03-02  
Effective tag: `gr-stage3-g11g12-v3-official`

## Scope

This note captures remaining known limitations after the official Stage-3 v3 governance switch and full 600-profile rerun confirmation.

## Current Official Readout

- Source package: `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/`
- Profiles: `600`
- Official Stage-3 pass: `597/600`
- Remaining fails: `3/600` (all in `G11`)
- `G12`: `600/600` on official v3 rerun

## Remaining Fail Classes (Strict Fail Scope)

Source taxonomy package:

- `05_validation/evidence/artifacts/gr-stage3-official-v3-failure-taxonomy-v1/`

Class split:

- `g11b_slope_instability`: `1`
- `weak_corr_multi_peak`: `1`
- `weak_corr_sparse_graph`: `1`

## Governance Notes

- No gate formula changes and no threshold edits were applied.
- Official v3 switch was governance-layer mapping over frozen runs (`G11/G12` from candidate-v3, `G7/G8/G9` inherited).
- Regression guard after rerun is `PASS` with zero mismatches.
