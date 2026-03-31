# QNG Stability Convergence Contract v2

Date locked: 2026-03-03  
Status: LOCKED

## Purpose

Strengthen convergence validation without threshold tuning by adding:

1. full vs bulk scoring
2. scaling-law trend check
3. cross-seed validation

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid:

- `n_nodes in {24, 30, 36, 42, 48}`
- `steps = 60`
- `seed_list = 3401..3420` (20 seeds)
- frozen edge/chi/noise/phi grids from stress-v1 defaults

## Observables

Primary error observable:

- `delta_energy_rel` median per `(seed, n_nodes)`

Support observable:

- `energy_noether_rel` p95 per `(seed, n_nodes)`

## Full vs Bulk Definition

- full levels: all `n_nodes` values
- bulk levels: drop smallest and largest level (`{30,36,42}`)

## Locked Checks (per-seed)

For each seed:

1. Full step fraction:
   - `fraction( median(n_{k+1}) <= median(n_k) + step_tol )`
   - pass if `>= full_step_fraction_min`
2. Bulk step fraction:
   - same rule on bulk levels
   - pass if `>= bulk_step_fraction_min`
3. Overall improvement:
   - `median(n_min) - median(n_max) >= overall_improvement_min`
4. Support sanity:
   - `p95_noether(n_max) / p95_noether(n_min) <= support_worsen_factor_max`
5. Scaling-law trend:
   - Spearman rho between `n_nodes` and median error
   - full pass if `rho_full <= rho_full_max`
   - bulk pass if `rho_bulk <= rho_bulk_max`

Locked constants:

- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `rho_bulk_max = -0.80`

## Gate Decision (aggregate across seeds)

Let:

- `full_seed_pass_fraction = fraction(seeds passing full checks)`
- `bulk_seed_pass_fraction = fraction(seeds passing bulk checks)`

Decision PASS if:

1. `full_seed_pass_fraction >= 0.85`
2. `bulk_seed_pass_fraction >= 0.85`
3. median `rho_full <= rho_full_max`
4. median `rho_bulk <= rho_bulk_max`

## Anti Post-Hoc Rules

1. No edits to constants or seed-list after seeing this run.
2. Any update requires `qng-stability-convergence-v3.md`.
3. This gate is convergence diagnostics only; no physics formula change.
