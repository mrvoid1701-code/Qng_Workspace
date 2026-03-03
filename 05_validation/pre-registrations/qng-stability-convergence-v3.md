# QNG Stability Convergence Contract v3 (Candidate)

Date locked: 2026-03-03  
Status: LOCKED (candidate-only, not executed in this commit)

## Purpose

v2 failed on bulk convergence while full convergence passed.  
v3 introduces a conceptual bulk definition change (core-stable bulk), without relaxing numeric thresholds.

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid (unchanged vs v2):

- `n_nodes in {24, 30, 36, 42, 48}`
- `steps = 60`
- `seed_list = 3401..3420` (20 seeds)
- frozen edge/chi/noise/phi grids from stress-v1 defaults

Primary observable:

- `delta_energy_rel` median per `(seed, n_nodes)`

Support observable:

- `energy_noether_rel` p95 per `(seed, n_nodes)`

## Full vs Core-Stable Bulk Definition

- full levels: all `n_nodes` values
- core-stable bulk levels: `{30, 36, 42}`
- a profile is eligible for core-stable bulk iff:
  - `active_regime_flag == pass`
  - `gate_sigma_bounds == pass`
  - `gate_metric_positive == pass`

Coverage requirement (data adequacy, not a physics threshold):

- each core bulk level must have at least `5` eligible profiles per seed
- otherwise seed is marked `insufficient_core_support` and bulk check fails

## Locked Checks (per-seed)

1. Full step fraction:
   - `fraction( median(n_{k+1}) <= median(n_k) + step_tol )`
   - pass if `>= full_step_fraction_min`
2. Core-bulk step fraction:
   - same rule on core-stable bulk levels
   - pass if `>= bulk_step_fraction_min`
3. Overall improvement:
   - `median(n_min) - median(n_max) >= overall_improvement_min`
4. Support sanity:
   - `p95_noether(n_max) / p95_noether(n_min) <= support_worsen_factor_max`
5. Scaling-law trend:
   - Spearman rho between `n_nodes` and median error
   - full pass if `rho_full <= rho_full_max`
   - core-bulk pass if `rho_bulk <= rho_bulk_max`

Locked constants (unchanged from v2):

- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `rho_bulk_max = -0.80`
- `full_seed_pass_fraction_min = 0.85`
- `bulk_seed_pass_fraction_min = 0.85`

## Gate Decision (aggregate across seeds)

Let:

- `full_seed_pass_fraction = fraction(seeds passing full checks)`
- `bulk_seed_pass_fraction = fraction(seeds passing core-bulk checks)`

Decision PASS if:

1. `full_seed_pass_fraction >= 0.85`
2. `bulk_seed_pass_fraction >= 0.85`
3. median `rho_full <= rho_full_max`
4. median `rho_bulk <= rho_bulk_max`

## Anti Post-Hoc Rules

1. No edits to constants/seed-list after this prereg.
2. Diagnostic outputs from:
   - `stability-convergence-v2-failure-taxonomy-v1`
   - `stability-convergence-v2-diagnostic-sweep-v1`
   are explanatory only and cannot be used to tune numeric thresholds.
3. Any change to thresholds or constants requires `qng-stability-convergence-v4.md`.
4. v3 remains candidate-only until a dedicated run record is added.
