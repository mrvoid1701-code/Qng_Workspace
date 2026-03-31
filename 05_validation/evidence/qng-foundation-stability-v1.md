# QNG Foundation Stability V1 - Evidence

Date: 2026-03-06

## Scope

This evidence verifies EL-consistency for the frozen stability lane
(`Sigma, chi, phi`) using:

- `03_math/derivations/qng-foundation-stability-v1.md`
- `05_validation/pre-registrations/qng-foundation-stability-tests-v1.md`
- `scripts/run_qng_el_consistency_v1.py`

## Verdict

`PASS`

All locked blocks passed:

- `STABILITY-PRIMARY`: `162/162`
- `STABILITY-ATTACK`: `162/162`
- `STABILITY-HOLDOUT`: `108/108`
- `ALL`: `432/432`

## Key Results

- `sigma_abs_p90` median by dataset:
  - primary: `0.003683`
  - attack: `0.003684`
  - holdout: `0.002993`
- worst observed residual:
  - `sigma_abs_max_max = 0.017621`
  - `global_abs_max_max = 0.017621`
- `chi_abs_max_max = 0.000000`
- `phi_abs_max_max = 0.000000`

Interpretation:

- Non-zero residual is dominated by bounded `Sigma` projection (`clip`).
- `chi` and `phi` channels are numerically consistent (machine-zero residual).

## Artifacts

- `05_validation/evidence/artifacts/qng-foundation-stability-v1/profile_residuals.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/summary.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/report.md`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/manifest.json`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/run-log.txt`
