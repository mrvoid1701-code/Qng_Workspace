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
5. Keep Stage-3 official baseline/guard frozen (`gr-stage3-g11-v5-official`) and enforce non-regression checks on reruns.
6. Preserve Stage-3 primary closure (`600/600`) while monitoring attack/holdout tails under preregistered estimator hardening (no threshold tuning).
7. Keep QM lane criteria separate from GR promotion criteria while Stage-2/Stage-3 official baselines remain frozen.
8. Maintain `QM-Stage-1` official policy freeze (`qm-stage1-g17b-v4-official`) and track remaining QM-lane fail classes with coupling audit checks.
9. Keep `QM-Stage-2` in prereg-only lane (`docs/QM_STAGE2_PREREG.md`) with strict post-v6 failure taxonomy (`qm-stage2-failure-taxonomy-post-v6-v1`) and single-gate candidate focus (`G18` first, prereg scaffold: `qm-stage2-g18-candidate-v4`).
10. Maintain coupling backbone evidence package (`qm-gr-coupling-audit-v2/bundle-v1`) as fixed pass reference (`2500/2500`, GR guard pre/post pass) while iterating QM candidates.
11. Harden the stability-term theory lane (`qng-stability-v1-strict`) with locked action/update definitions and preregistered stress invariants.
12. Close stability fail taxonomy (`stability-v1`) and evaluate candidate energy observables under preregistered non-degradation policy.
13. Execute targeted `G18` candidate lane from post-v6 Stage-2 findings using prereg scaffold `qm-stage2-g18-candidate-v4` (no threshold tuning, degraded=0 required).

## Non-Goals for Housekeeping Passes

- no scientific formula changes
- no gate threshold changes
- no retroactive rewriting of historical evidence logs/manifests
