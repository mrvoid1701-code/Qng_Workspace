# QNG Stability Convergence v5 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v5.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v5/raw/summary.csv`

Gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v5/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v5/report.json`

## Locked Parameters Used

- levels: `24,28,32,36,40,44,48` (bulk: `28,32,36,40,44`)
- full metric: `delta_energy_rel`
- bulk metric: `delta_energy_rel`
- trend estimator: `Kendall tau + bootstrap CI`
- `bulk_bootstrap_reps = 400`
- `bulk_ci_alpha = 0.05`
- pass rule: `tau_ci_high < 0`
- unchanged lane thresholds from v4

## Result Snapshot

- decision: `FAIL`
- seed_count: `20`
- `full_seed_pass_fraction = 0.45` (FAIL vs 0.85)
- `bulk_seed_pass_fraction = 0.00` (FAIL vs 0.85)
- `bulk_ci_pass_fraction = 0.10`
- `rho_full_median = -0.785714` (PASS vs -0.60)
- `tau_bulk_median = -0.600000`
- `tau_bulk_ci_high_median = 0.200000` (FAIL; expected `< 0`)
- `insufficient_bulk_support_seed_count = 0`

## Governance Note

No threshold changes were made.  
v5 did not pass under locked thresholds; no promotion/freeze/baseline switch is authorized.
