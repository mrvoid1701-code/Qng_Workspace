# GR Stage-1 Freeze (Internal Release)

Date: 2026-03-02  
Stage ID: `GR-Stage-1`  
Release type: internal freeze

## Scope

`GR-Stage-1` covers weak-field + PPN + action-closure behavior through gates `G10..G16`.

Core decision policy in this frozen stage:

- `G15b official`: `G15b-v2` (potential-quantile Shapiro proxy)
- `G15b legacy diagnostic`: `G15b-v1`
- `G16b official`: hybrid policy (low-signal -> `v2`, high-signal -> `v1`)
- `G16b legacy diagnostic`: `v1`

## Guarantees

This freeze guarantees:

1. Reproducible official GR-chain checks from clean clone using documented commands.
2. Official baseline guard against:
   - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
3. Frozen governance for `G15b` and `G16b` decision logic (official vs diagnostic vs candidate).

## Explicit Non-Claims

This freeze does not claim:

1. strong-field completeness,
2. full `3+1` formal closure coverage,
3. full tensor-mode completion as official GR claim scope.

Those move to `GR-Stage-2` prereg and are evaluated separately before any promotion.

## Freeze Pointers

- status snapshot: `docs/GR_STATUS.md`
- scope commitments: `docs/GR_COMMITMENTS.md`
- reproducibility commands: `docs/REPRODUCIBILITY.md`
- gate map: `docs/GATES.md`

## Release Tag

Internal freeze tag: `gr-stage1-freeze-2026-03-02`
