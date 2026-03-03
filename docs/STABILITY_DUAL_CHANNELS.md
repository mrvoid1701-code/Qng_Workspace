# Stability Dual Channels

Date: 2026-03-03  
Status: governance lock (diagnostic + candidate-policy framing)

## Scope

Stability evidence indicates two separable channels:

- `S1` energetic channel (energy drift/trend behavior)
- `S2` structural channel (boundedness, metric positivity/conditioning, locality, residual consistency)

This document freezes the interpretation layer only.  
It does not change physics equations or existing official thresholds.

## Channel Definitions

### S2 Structural (Deterministic Lane)

S2 is evaluated from non-energy hard gates:

- `gate_sigma_bounds`
- `gate_metric_positive`
- `gate_metric_cond`
- `gate_runaway`
- `gate_variational_residual`
- `gate_alpha_drift`
- `gate_no_signalling`

Observed on latest convergence packages (`v4`, `v5`): structural pass is saturated (`1.0` profile/seed pass fractions).

### S1 Energetic (Statistical Lane)

S1 is evaluated from energy trend observables:

- per-profile energy drift (`delta_energy_rel`)
- per-seed trend summaries (`bulk_tau`, CI, slopes)
- convergence trend checks over resolution levels

Observed on latest convergence packages (`v4`, `v5`): energetic lane drives failures.

## Governance Rule

Convergence must be reported as:

1. `S2 structural status` (hard deterministic gate status)
2. `S1 energetic status` (statistical trend status)

A global convergence verdict is valid only if both are explicitly reported.

## Anti Post-Hoc

1. No retrospective threshold edits in S1 or S2.
2. Any S1 estimator change requires a new prereg version.
3. S2 gate set may only change via explicit prereg and change record.

## References

- `05_validation/evidence/artifacts/stability-dual-attributes-v1/`
- `05_validation/evidence/artifacts/stability-convergence-v4/`
- `05_validation/evidence/artifacts/stability-convergence-v5/`
