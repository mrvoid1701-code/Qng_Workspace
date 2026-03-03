# QNG Stability Convergence v6 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v6.md`

## Execution

Source sweep:

- `05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv`

Gate outputs:

- `05_validation/evidence/artifacts/stability-convergence-v6/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6/report.json`

## Locked Parameters Used

- levels: `24,28,32,36,40,44,48` (bulk: `28,32,36,40,44`)
- full metric: `delta_energy_rel`
- bulk metric: `delta_energy_rel`
- S2 lane: deterministic hard gates unchanged
- S1 lane: median Theil-Sen slope across seeds + bootstrap CI
- `bootstrap_reps = 2000`
- `ci_alpha = 0.05`
- pass rule: S2 all-pass and S1 CI upper bounds `< 0`

## Result Snapshot

- decision: `PASS`
- seed_count: `20`
- `s2_seed_pass_fraction = 1.000000` (PASS)
- `bulk_valid_seed_fraction = 1.000000` (PASS)
- `full_slope_median = -0.000603708`
- `full_slope_ci = [-0.000655079, -0.000497396]` (PASS)
- `bulk_slope_median = -0.000592055`
- `bulk_slope_ci = [-0.000736055, -0.000410758]` (PASS)

## Duration Note

Correction: the previously noted `~5 hours` duration belongs to a different prior test batch, not this v6 convergence run.

## Governance Note

No threshold changes were made.  
v6 remains candidate evidence until an explicit governance switch commit is made.
