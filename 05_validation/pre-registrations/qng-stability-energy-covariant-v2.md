# QNG Stability Energy Gate Candidate v2 - Pre-registration

- Date locked: 2026-03-03
- Status: LOCKED (candidate lane)
- Depends on:
  - `qng-stability-v1-strict`
  - `scripts/tools/run_stability_stress_v1.py`
  - `scripts/tools/analyze_stability_v1_failures_v1.py`

## Motivation

v1 taxonomy indicates fail concentration in `gate_energy_drift`.
Candidate-v2 tests whether a covariant/Noether-like energy diagnostic is a better
stability observable than raw gate-energy drift, without changing non-energy gates.

## Frozen Evaluation Protocol

Primary grid:

- same v1 strict case grid (`54` cases) and same seeds.

Attack grid:

- same parameter axes with doubled seeds per case (`2x` seed block).

Holdout grid:

- same axes with perturbed node count and steps:
  - `n_nodes in {30, 42}`
  - `steps in {80}`

## Decision Policy (Candidate-Only)

1. Keep all non-energy gates unchanged from v1.
2. Evaluate candidate energy metric in parallel (no official switch yet).
3. Promotion constraints:
   - `degraded=0` on all non-energy gates vs v1
   - energy-gate uplift on v1 fail-cases
   - no drop in cases where v1 energy gate already passes

## Anti Post-Hoc Rules

1. No threshold edits after viewing primary results.
2. Any threshold/protocol change requires new prereg version (`...-v3.md`).
3. Official switch allowed only after primary + attack + holdout pass.
