# G16b Hybrid Promotion Pre-Registration (v1)

Date: 2026-03-01

Scope: promotion protocol for the `G16b` hybrid candidate:

- low-signal regime: use `G16b-v2` decision
- high-signal regime: keep legacy `G16b-v1` decision

This document freezes promotion criteria before additional confirmation runs.

## Frozen Definition

Base definition source:

- `scripts/tools/run_g16b_split_hybrid_v1.py`

Hybrid decision rule:

- `is_low_signal=true` -> `g16b_hybrid = g16b_v2`
- `is_low_signal=false` -> `g16b_hybrid = g16b_v1`

Low-signal flag source (already frozen in v2 prereg):

- `is_low_signal = (std(T11)/|mean(T11)| > 10)`

No formula or threshold changes in:

- `scripts/run_qng_action_v1.py`

## Promotion Grid (Primary)

- datasets: `DS-002, DS-003, DS-006`
- seeds: `3401..3600`
- `phi_scale=0.08`
- input summary:
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`

## Promotion Criteria (must all pass)

1. `degraded_vs_v1 = 0` (global)
2. per-dataset non-degradation:
   - for each dataset, `hybrid_pass >= v1_pass`
3. high-signal non-degradation:
   - `hybrid_fail_high <= v1_fail_high`
4. low-signal improvement:
   - `hybrid_fail_low < v1_fail_low`
5. minimum global uplift:
   - `(hybrid_pass_rate - v1_pass_rate) >= 2.0 percentage points`

Evaluator:

- `scripts/tools/evaluate_g16b_hybrid_promotion_v1.py`

## Attack Tests (anti post-hoc)

To reject "chosen to pass" criticism, run frozen protocol unchanged on:

1. Seed-range extension:
   - datasets: `DS-002, DS-003, DS-006`
   - seeds: `3601..4100` (500 seeds per dataset)
   - `phi_scale=0.08`

2. Holdout datasets (generated variant):
   - datasets: `DS-004, DS-008`
   - seeds: `3401..3600`
   - `phi_scale=0.08`

Attack-test acceptance:

- same criteria as primary grid, except strict dataset list is adapted to test set.
- no threshold/definition edits allowed between primary and attack runs.

## Promotion Decision Policy

- If primary grid and both attack tests pass -> promote hybrid to official `G16b` decision gate.
- If any test fails -> keep `G16b-v1` official and keep hybrid candidate-only.

## Execution Record (2026-03-01)

Evaluation outputs:

- Primary:
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- Attack A (seed range 3601..4100):
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- Attack B (holdout DS-004/008):
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

Observed decisions:

- primary: `PASS`
- attack A: `PASS`
- attack B: `PASS`

Result:

- prereg criteria satisfied across all required runs.
- hybrid was marked `PROMOTION-READY` and is now promoted to official `G16b` decision gate (switch commit dated `2026-03-02`).
