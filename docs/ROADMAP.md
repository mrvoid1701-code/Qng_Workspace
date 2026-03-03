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
8. Maintain `QM-Stage-1` official policy freeze (`qm-stage1-g18-v2-official`) and track remaining QM-lane fail classes with coupling audit checks.
9. Keep `QM-Stage-2` in prereg-only lane (`docs/QM_STAGE2_PREREG.md`) using frozen block protocol + coupling stability checks before any governance switch.
10. Harden the stability-term theory lane (`qng-stability-v1-strict`) with locked action/update definitions and preregistered stress invariants.
11. Close stability fail taxonomy (`stability-v1`) and evaluate candidate energy observables under preregistered non-degradation policy.

## Non-Goals for Housekeeping Passes

- no scientific formula changes
- no gate threshold changes
- no retroactive rewriting of historical evidence logs/manifests
