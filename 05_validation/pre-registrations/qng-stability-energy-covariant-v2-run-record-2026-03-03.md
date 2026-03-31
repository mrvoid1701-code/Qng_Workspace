# QNG Stability Energy Candidate-v2 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-energy-covariant-v2.md`

## Protocol Lock Confirmation

- Energy threshold used by candidate-v2: `0.90` (unchanged from v1 gate).
- Non-energy gates unchanged.
- Decision checks (all blocks):
  - `degraded=0` on energy pass-cases
  - `non_energy_stable=true`
  - `energy_uplift=true`

## Evidence Packages

Primary:

- source: `05_validation/evidence/artifacts/stability-v1-prereg-v2/primary_s3401/summary.csv`
- candidate: `05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401/summary.csv`
- promotion: `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/primary_s3401/report.json`

Attack:

- source: `05_validation/evidence/artifacts/stability-v1-prereg-v2/attack_s3401_4401/summary.csv`
- candidate: `05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401/summary.csv`
- promotion: `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/attack_s3401_4401/report.json`

Holdout:

- source: `05_validation/evidence/artifacts/stability-v1-prereg-v2/holdout_n30_42_s3401/summary.csv`
- candidate: `05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401/summary.csv`
- promotion: `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/holdout_n30_42_s3401/report.json`

Bundle decision:

- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/promotion_decision.md`
- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/promotion_decision.json`

## Results Snapshot

- Primary (`n=54`): `PASS`, energy improved `10`, degraded `0`, all-pass improved `10`, non-energy degraded `0`.
- Attack (`n=108`): `PASS`, energy improved `18`, degraded `0`, all-pass improved `18`, non-energy degraded `0`.
- Holdout (`n=108`): `PASS`, energy improved `52`, degraded `0`, all-pass improved `52`, non-energy degraded `0`.
- Bundle: `PASS` (`3/3` blocks passed).

## Governance Note

This run record is execution-only. It does not switch official stability gate policy.
Any official switch requires a separate governance commit and explicit policy update.
