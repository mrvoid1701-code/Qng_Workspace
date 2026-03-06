# RESULT: D4 Stage-2 Dual-Kernel v1

Date: 2026-03-06

## Verdict

`HOLD`

## What Was Tested

- Locked split (by galaxy ID): seed `3401`, train fraction `0.70`
- Locked constants: `s1_lambda=0.28`, `s2_const=0.355`, `r0_kpc=1.0`
- Locked search grids:
  - `tau in {0.5,1,2,3,5,8,12,20,30,50}`
  - `alpha in {0.3,0.5,0.7,1.0,1.3}`
- Non-circular rule: kernels depend only on radius + baryon term (no `v_obs` in kernels)

## Key Numbers

- holdout `chi2/N`:
  - `null = 270.776399`
  - `MOND = 46.690217`
  - `dual-kernel = 241.639903`
- holdout improve vs null: `10.760353%`
- holdout worse vs MOND: `417.538620%`
- train/holdout improvement gap: `0.491749 pp`
- best train-selected parameters:
  - `tau=0.5`, `alpha=0.3`, `k1=0.163458892`, `k2=0.0`

## Interpretation

- The dual-kernel model is stable and generalizes (small train/holdout gap).
- It improves over null baseline.
- It remains far behind MOND on this DS-006 real-data benchmark.
- `k2=0.0` at optimum indicates the current Stage-2 fit does not yet exploit the structural kernel component in a useful way.

## Next Non-Post-Hoc Step

Keep v1 frozen and move to `d4-stage2-dual-kernel-v2` only via new prereg:

1. Change one conceptual element at a time (kernel family or fitting objective).
2. Keep split/governance fixed.
3. Re-run same evaluator with degraded checks.

## Evidence

- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/`
- `05_validation/pre-registrations/d4-stage2-dual-kernel-v1.md`
- `05_validation/pre-registrations/d4-stage2-dual-kernel-v1-run-record-2026-03-06.md`
