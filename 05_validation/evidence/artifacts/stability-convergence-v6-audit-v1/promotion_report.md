# Stability Convergence v6 Promotion Eval v1

- eval_id: `stability-convergence-v6-promotion-eval-v1`
- generated_utc: `2026-03-03T15:21:00.547664+00:00`
- audit_root: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v6-audit-v1`
- decision: `PASS`

## Guard Checks

- zero_degraded_seed: `true`
- all_v6_blocks_pass: `true`
- holdout_shift_block_pass: `true`
- no_seed_set_mismatch: `true`
- s2_all_blocks_ok: `true`
- s1_ci_all_blocks_ok: `true`
- no_positive_seed_slopes: `false`

## Notes

- Legacy comparator is v5-like convergence gate (run via v4 engine with frozen v5 constants).
- v6 seed diagnostics use strict per-seed slope sign (`full<0`, `bulk<0`) plus structural/bulk-valid flags.
- `no_positive_seed_slopes` is an anti-masking check (guards against median-only wins hiding positive-slope seeds).
