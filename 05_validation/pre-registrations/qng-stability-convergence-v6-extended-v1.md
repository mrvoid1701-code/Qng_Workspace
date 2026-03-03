# QNG Stability Convergence v6 Extended Audit v1 (Post-Freeze)

Date locked: 2026-03-03  
Status: LOCKED (execution pending)

## Purpose

Run a larger post-freeze robustness audit for official convergence policy `v6` on 3 fixed blocks (primary, attack, shifted holdout), with no formula or threshold edits.

## Fixed Blocks

1. Primary block
   - dataset-id: `STABILITY-CONVERGENCE-V6-EXT-PRIMARY`
   - seeds: `3401..3600` (200 seeds)
   - `n_nodes`: `24,28,32,36,40,44,48`
   - `steps`: `60`

2. Attack block
   - dataset-id: `STABILITY-CONVERGENCE-V6-EXT-ATTACK`
   - seeds: `3601..3800` (200 seeds)
   - `n_nodes`: `24,28,32,36,40,44,48`
   - `steps`: `60`

3. Shifted holdout block
   - dataset-id: `STABILITY-CONVERGENCE-V6-EXT-HOLDOUT`
   - seeds: `3801..4000` (200 seeds)
   - `n_nodes`: `30,36,42,48`
   - `steps`: `80`
   - shifted stress grid:
     - `edge_prob_grid`: `0.05,0.12,0.25`
     - `chi_scale_grid`: `0.40,1.00,1.80`
     - `noise_grid`: `0.00,0.02,0.05`
     - `phi_shock_grid`: `0.00,0.60`

## Fixed Evaluation Policy

Comparator and decision policy are frozen:

- legacy comparator: `v5-like` (`run_stability_convergence_gate_v4.py` with v5 constants)
- official policy: `run_stability_convergence_gate_v6.py`
- evaluator: `evaluate_stability_convergence_v6_promotion_v1.py`

No threshold tuning or formula edits are allowed in this audit.

## Expected Outputs

- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/`
  - per-block raw, legacy, v6 candidate packages
  - `block_summary.csv`
  - `promotion_report.md`
  - `promotion_report.json`
  - `manifest.json`
  - `run-log.txt`

## Anti Post-Hoc Rules

1. Block definitions and seed ranges are locked above.
2. No edits to v6 policy, legacy comparator thresholds, or stress formulas during run.
3. Any change requires a new prereg version (`v6-extended-v2` or later).
