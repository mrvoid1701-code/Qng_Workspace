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
5. Execute `GR-Stage-2` prereg lane (strong-field + 3+1 coverage expansion + tensor-mode checks) with frozen protocol.
6. Keep QM lane criteria separate from GR promotion criteria until Stage-2 is closed.

## Non-Goals for Housekeeping Passes

- no scientific formula changes
- no gate threshold changes
- no retroactive rewriting of historical evidence logs/manifests
