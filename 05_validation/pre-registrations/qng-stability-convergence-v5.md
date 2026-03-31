# QNG Stability Convergence Contract v5 (Candidate)

Date locked: 2026-03-03  
Status: LOCKED (candidate-only)

## Purpose

Address statistical-power limits observed in v4 by increasing resolution levels while keeping estimator and thresholds fixed.

## Single Conceptual Change (Locked)

Only one conceptual change is allowed in v5:

- increase level count from 5 total (3 bulk) to 7 total (5 bulk):
  - full levels: `{24,28,32,36,40,44,48}`
  - bulk levels: `{28,32,36,40,44}`

Everything else remains the same as v4.

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid:

- `n_nodes in {24, 28, 32, 36, 40, 44, 48}`
- `steps = 60`
- `seed_list = 3401..3420` (20 seeds)

Observables:

- full metric: `delta_energy_rel`
- bulk metric: `delta_energy_rel`
- support metric: `energy_noether_rel`

Bulk eligibility (unchanged):

- `active_regime_flag == pass`
- `gate_sigma_bounds == pass`
- `gate_metric_positive == pass`
- `core_stable_size >= 6`
- `core_stable_ratio >= 0.10`
- and `n_profiles_bulk_eligible >= 5` per bulk level

Trend estimator (unchanged from v4):

- `Kendall tau + bootstrap CI`
- `bulk_bootstrap_reps = 400`
- `bulk_ci_alpha = 0.05`
- per-seed bulk trend pass if `tau_ci_high < 0`

## Locked Thresholds (unchanged)

- `step_tol = 0.002`
- `full_step_fraction_min = 0.75`
- `bulk_step_fraction_min = 0.85`
- `overall_improvement_min = 0.005`
- `support_worsen_factor_max = 1.25`
- `rho_full_max = -0.60`
- `full_seed_pass_fraction_min = 0.85`
- `bulk_seed_pass_fraction_min = 0.85`

## Gate Decision (aggregate across seeds)

Decision PASS if:

1. `full_seed_pass_fraction >= 0.85`
2. `bulk_seed_pass_fraction >= 0.85`
3. median `rho_full <= rho_full_max`
4. median `tau_bulk_ci_high < 0`

## Anti Post-Hoc Rules

1. No threshold or seed/grid edits after this prereg.
2. Any further logic change requires `qng-stability-convergence-v6.md`.
3. v5 remains candidate-only until run record exists.
