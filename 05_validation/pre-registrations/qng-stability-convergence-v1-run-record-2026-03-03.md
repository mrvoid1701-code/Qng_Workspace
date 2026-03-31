# QNG Stability Convergence v1 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v1.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v1/raw/summary.csv`

Convergence gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v1/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v1/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v1/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v1/report.json`

## Locked Parameters Used

- `step_tol = 0.002`
- `min_step_pass_fraction = 0.75`
- `min_overall_improvement = 0.005`
- `support_worsen_factor_max = 1.25`

## Result Snapshot

- decision: `PASS`
- step_pass_fraction: `0.75`
- overall_improvement (`coarse-fine`): `0.017213`
- support_ratio (`p95_fine/p95_coarse`): `1.055047`
