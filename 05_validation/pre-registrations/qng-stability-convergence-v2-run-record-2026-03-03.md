# QNG Stability Convergence v2 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v2.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv`

Gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v2/report.json`

## Locked Parameters Used

- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `rho_bulk_max = -0.80`
- `full_seed_pass_fraction_min = 0.85`
- `bulk_seed_pass_fraction_min = 0.85`

## Result Snapshot

- decision: `FAIL`
- seed_count: `20`
- `full_seed_pass_fraction = 0.90` (PASS vs 0.85)
- `bulk_seed_pass_fraction = 0.50` (FAIL vs 0.85)
- `rho_full_median = -0.90` (PASS vs -0.60)
- `rho_bulk_median = -0.75` (FAIL vs -0.80)

## Governance Note

No constants were changed after this result. Any adjustment requires new prereg version.
