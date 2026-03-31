# QNG Stability Convergence Contract v4 (Candidate)

Date locked: 2026-03-03  
Status: LOCKED (candidate-only)

## Purpose

Keep Sigma-mask core-stable bulk definition, but replace fragile bulk trend estimator with a robust statistical estimator.

## Single Conceptual Change (Locked)

Only one conceptual change is allowed in v4:

- bulk trend decision uses `Kendall tau + bootstrap CI` instead of direct rank threshold on raw bulk series.

Explicitly out-of-scope for v4:

- no threshold relaxation on existing lane constants
- no seed/grid changes
- no change to full-trend estimator
- no change to bulk metric field

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid (unchanged):

- `n_nodes in {24, 30, 36, 42, 48}`
- `steps = 60`
- `seed_list = 3401..3420` (20 seeds)

Observables:

- full metric: `delta_energy_rel`
- bulk metric: `delta_energy_rel`
- support metric: `energy_noether_rel`

Bulk eligibility:

- `active_regime_flag == pass`
- `gate_sigma_bounds == pass`
- `gate_metric_positive == pass`
- `core_stable_size >= 6`
- `core_stable_ratio >= 0.10`
- and `n_profiles_bulk_eligible >= 5` per bulk level

## Locked Checks (per-seed)

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
5. Full trend:
   - `rho_full <= rho_full_max` (unchanged)
6. Bulk robust trend:
   - compute `tau_bulk` on bulk-level medians
   - bootstrap CI on tau with `reps=400`, `alpha=0.05`
   - bulk trend pass if `tau_ci_high < 0`

Locked constants:

- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `full_seed_pass_fraction_min = 0.85`
- `bulk_seed_pass_fraction_min = 0.85`
- `bulk_bootstrap_reps = 400`
- `bulk_ci_alpha = 0.05`

## Gate Decision (aggregate across seeds)

Decision PASS if:

1. `full_seed_pass_fraction >= 0.85`
2. `bulk_seed_pass_fraction >= 0.85`
3. median `rho_full <= rho_full_max`
4. median `tau_bulk_ci_high < 0`

## Anti Post-Hoc Rules

1. No edits to thresholds/seed-list after this prereg.
2. Any threshold changes require `qng-stability-convergence-v5.md`.
3. v4 remains candidate-only until run record is added.
