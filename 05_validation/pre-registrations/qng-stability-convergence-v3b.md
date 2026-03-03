# QNG Stability Convergence Contract v3b (Candidate)

Date locked: 2026-03-03  
Status: LOCKED (candidate-only)

## Purpose

v3 (Sigma-mask eligibility) did not change aggregate outcome vs v2 on the same 20-seed block.  
v3b changes exactly one concept: bulk uses a connected-central-component energy drift observable, not the global drift observable.

## Single Conceptual Change (Locked)

Only one conceptual change is allowed in v3b:

- bulk metric field switches from `delta_energy_rel` to `delta_energy_rel_core_cc`
  where:
  - core nodes are defined by `sigma_i >= mean(sigma)` at final state
  - anchor node is `argmax sigma_i`
  - central connected component is the connected component containing anchor in the induced core-node subgraph
  - `delta_energy_rel_core_cc` is computed on that fixed component between start/end states

Explicitly out-of-scope for v3b:

- no threshold relaxation
- no seed/grid change
- no connected-component threshold tuning
- no robust-regression switch

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid (unchanged):

- `n_nodes in {24, 30, 36, 42, 48}`
- `steps = 60`
- `seed_list = 3401..3420` (20 seeds)
- frozen edge/chi/noise/phi grids from stress-v1 defaults

Full observable (unchanged):

- `delta_energy_rel` median per `(seed, n_nodes)`

Bulk observable (changed):

- `delta_energy_rel_core_cc` median per `(seed, n_nodes)` on levels `{30,36,42}`

Support observable:

- `energy_noether_rel` p95 per `(seed, n_nodes)`

## Locked Checks (per-seed)

1. Full step fraction:
   - `fraction( median(n_{k+1}) <= median(n_k) + step_tol )`
   - pass if `>= full_step_fraction_min`
2. Bulk step fraction:
   - same rule on bulk levels, but with bulk metric
   - pass if `>= bulk_step_fraction_min`
3. Overall improvement:
   - `median(n_min) - median(n_max) >= overall_improvement_min` (full metric)
4. Support sanity:
   - `p95_noether(n_max) / p95_noether(n_min) <= support_worsen_factor_max`
5. Scaling-law trend:
   - full pass if `rho_full <= rho_full_max` (full metric)
   - bulk pass if `rho_bulk <= rho_bulk_max` (bulk metric)

Locked constants (unchanged from v2/v3):

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

## Gate Decision (aggregate across seeds)

Decision PASS if:

1. `full_seed_pass_fraction >= 0.85`
2. `bulk_seed_pass_fraction >= 0.85`
3. median `rho_full <= rho_full_max`
4. median `rho_bulk <= rho_bulk_max`

## Anti Post-Hoc Rules

1. No edits to thresholds or seed/grid after this prereg.
2. Any threshold change requires `qng-stability-convergence-v4.md`.
3. v3b remains candidate-only until run record is written.
