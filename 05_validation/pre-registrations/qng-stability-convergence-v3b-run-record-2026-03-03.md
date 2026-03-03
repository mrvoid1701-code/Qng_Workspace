# QNG Stability Convergence v3b - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v3b.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v3b/raw/summary.csv`

Gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v3b/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v3b/report.json`

## Locked Parameters Used

- full metric field: `delta_energy_rel`
- bulk metric field: `delta_energy_rel_core_cc`
- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `rho_bulk_max = -0.80`
- `full_seed_pass_fraction_min = 0.85`
- `bulk_seed_pass_fraction_min = 0.85`
- `bulk_min_profiles_per_level = 5`

## Result Snapshot

- decision: `FAIL`
- seed_count: `20`
- `full_seed_pass_fraction = 0.90` (PASS vs 0.85)
- `bulk_seed_pass_fraction = 0.45` (FAIL vs 0.85)
- `rho_full_median = -0.90` (PASS vs -0.60)
- `rho_bulk_median = -0.50` (FAIL vs -0.80)
- `insufficient_bulk_support_seed_count = 0`

## Governance Note

No thresholds were changed.  
v3b did not improve convergence outcome vs v2/v3, so no promotion/freeze/baseline switch is authorized.
