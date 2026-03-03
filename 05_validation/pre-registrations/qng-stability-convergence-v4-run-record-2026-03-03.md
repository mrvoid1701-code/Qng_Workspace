# QNG Stability Convergence v4 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v4.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv`

Gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v4/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v4/report.json`

## Locked Parameters Used

- full metric: `delta_energy_rel`
- bulk metric: `delta_energy_rel`
- trend estimator: `Kendall tau + bootstrap CI`
- `bulk_bootstrap_reps = 400`
- `bulk_ci_alpha = 0.05`
- pass rule: `tau_ci_high < 0`
- `bulk_min_profiles_per_level = 5`
- `bulk_core_size_min = 6`
- `bulk_core_ratio_min = 0.10`
- plus unchanged lane thresholds from v2/v3

## Result Snapshot

- decision: `FAIL`
- seed_count: `20`
- `full_seed_pass_fraction = 0.90` (PASS vs 0.85)
- `bulk_seed_pass_fraction = 0.15` (FAIL vs 0.85)
- `bulk_ci_pass_fraction = 0.15`
- `rho_full_median = -0.90` (PASS vs -0.60)
- `tau_bulk_median = -0.666667`
- `tau_bulk_ci_high_median = 0.333333` (FAIL; expected `< 0`)
- `insufficient_bulk_support_seed_count = 0`

## Governance Note

No threshold changes were made.  
Because v4 underperformed vs v2/v3/v3b, no promotion/freeze/baseline switch is authorized.
