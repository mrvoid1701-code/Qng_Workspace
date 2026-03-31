# QNG Stability Convergence Contract v1

Date locked: 2026-03-03  
Status: LOCKED

## Purpose

Define a minimal, non-post-hoc convergence check from discrete refinement toward
continuum behavior for the stability lane.

## Fixed Protocol

Source runner:

- `scripts/tools/run_stability_stress_v1.py`

Grid:

- `n_nodes in {24, 30, 36, 42, 48}`
- `steps = 60`
- `seed = 3401`
- same parameter grids for edge/chi/noise/phi as frozen stress-v1 defaults.

## Convergence Observable

Primary convergence observable (legacy discretization-sensitive drift):

- `delta_energy_rel` median per `n_nodes`.

Support observable (official covariant drift sanity):

- `energy_noether_rel` p95 per `n_nodes`.

## Gate Rule (locked)

Let `M(n)` be median `delta_energy_rel` at resolution `n`.
For consecutive levels `(n_k, n_{k+1})`:

- step passes if `M(n_{k+1}) <= M(n_k) + step_tol`, with `step_tol = 0.002`.

Pass criteria:

1. step-pass fraction `>= 0.75`
2. overall improvement: `M(n_max) <= M(n_min) - 0.005`
3. support sanity: `p95_noether(n_max) <= 1.25 * p95_noether(n_min)`

## Anti Post-Hoc Rules

1. no parameter/threshold edits after seeing this run
2. any change requires `qng-stability-convergence-v2.md`
3. this gate is additive diagnostics; it does not modify physics formulas
