# QNG Foundation Stability V2 - Evidence

Date: 2026-03-06

## Scope

Hardened EL-consistency verification for frozen stability lane (`Sigma, chi, phi`)
using independent `U_current` vs `U_EL` comparison and joint global residual metric.

References:

- `05_validation/pre-registrations/qng-foundation-stability-tests-v2.md`
- `03_math/derivations/qng-foundation-stability-v1.md`
- `scripts/run_qng_el_consistency_v1.py`

## Verdict

`PASS`

Block results:

- `STABILITY-PRIMARY`: `162/162`
- `STABILITY-ATTACK`: `162/162`
- `STABILITY-HOLDOUT`: `108/108`
- `ALL`: `432/432`

## Key Metrics

- `profile_sigma_abs_max_max = 0.000000`
- `profile_global_abs_max_max = 0.000000` (`global` from `R_joint`)
- `profile_chi_abs_max_max = 0.000000`
- `profile_phi_abs_max_max = 0.000000`

Interpretation:

- For tested blocks, `U_current` and independent `U_EL` implementations are
  numerically consistent to machine precision.
- No channel-dilution artifact is used in `global_abs_*` (joint max metric).

## Artifacts

- `05_validation/evidence/artifacts/qng-foundation-stability-v2/profile_residuals.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/summary.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/report.md`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/manifest.json`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/run-log.txt`
