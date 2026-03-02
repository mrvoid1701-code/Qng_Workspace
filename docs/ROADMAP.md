# ROADMAP

## Current Stage

QNG workspace is in a reproducibility-hardening phase:

- core validation matrix and results log are established
- evidence registry is populated (`05_validation/evidence/`)
- GR/QM bridge chain has dedicated runners (`G10..G20`)
- layout and runner CLI were standardized for repeatable execution
- `GR-Stage-1` (weak-field + PPN + action closure) is now frozen as internal release scope

## Current Priorities

1. Keep P1/P2 reruns locked and reproducible (no threshold drift).
2. Replace placeholder holdout residual rows with publication-grade values where still pending.
3. Extend public-ready export bundles in `07_exports/` from locked evidence.
4. Keep run manifests and keepfiles policy aligned when adding new gates/runners.
5. Keep Stage-3 official baseline/guard frozen (`gr-stage3-g11g12-v3-official`) and enforce non-regression checks on reruns.
6. Track remaining Stage-3 official fail classes (`3/600`, all `G11`) via preregistered estimator hardening (no threshold tuning).
7. Keep QM lane criteria separate from GR promotion criteria while Stage-2/Stage-3 official baselines remain frozen.

## Non-Goals for Housekeeping Passes

- no scientific formula changes
- no gate threshold changes
- no retroactive rewriting of historical evidence logs/manifests
