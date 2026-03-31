# Stability Energy V2 Official Switch

Date: 2026-03-03  
Policy ID: `stability-official-v2`  
Effective tag: `stability-energy-v2-official`

## Decision

Promote energy candidate-v2 from candidate lane to official decision policy for
the stability lane.

## Scope

Official mapping applies to stability evidence summaries only:

- legacy energy status: `gate_energy_drift_v1`
- candidate energy status: `gate_energy_drift_v2`
- official energy status: `gate_energy_drift = gate_energy_drift_v2`
- legacy all-pass: `all_pass_v1`
- official all-pass: `all_pass_stability = all_pass_v2`

Non-energy gates remain unchanged.

## Governance Constraints

1. No formula edits.
2. No threshold edits.
3. Switch is policy-layer only, applied on frozen candidate summaries.
4. Legacy statuses remain preserved for diagnostics.

## Runner

- `scripts/tools/run_stability_official_v2.py`

## Apply Targets

- `stability_official_apply_primary`
- `stability_official_apply_attack`
- `stability_official_apply_holdout`

## Evidence Prerequisites

This switch depends on candidate-v2 promotion evidence:

- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/promotion_decision.md`
