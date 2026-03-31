# QM G18 Candidate-v2 Pre-Registration (Hybrid Local d_s for Multi-Peak)

Date: 2026-03-03  
Status: `candidate-only` (G18-v1 remains legacy baseline)

## Why This Candidate Exists

Post-switch QM Stage-1 taxonomy (`qm-stage1-failure-taxonomy-v1` and strict `G18` taxonomy) shows:

- dominant failing gate in QM lane failures: `G18`
- strict G18 subgate dominance: `G18d` (spectral-dimension check)
- fail signatures are concentrated in multi-peak regimes

This candidate addresses estimator robustness in multi-peak regimes without editing core gate formulas or thresholds.

## One-Line Gate Clarification (G18d)

`G18d` validates emergent geometry via spectral dimension `d_s` from random-walk return scaling.

## Candidate Definition (Hybrid)

Baseline remains frozen:

- `G18-v1` gate logic and thresholds unchanged in core runner

Candidate update applies only to `G18d`:

1. If `G18d-v1` is `pass` -> keep `G18d-v2=pass`.
2. If `G18d-v1` is `fail` and profile is multi-peak:
   - compute local `d_s` on peak-local basins (topological neighborhood per dominant peaks),
   - aggregate robustly using median of valid local `d_s` estimates,
   - apply the same `G18d` threshold band as v1 (from metric file, default `(1.2, 3.5)`).
3. If not multi-peak -> keep `fail`.

No threshold tuning of gate formulas is allowed.

## Frozen Parameters

- multi-peak detector:
  - `sigma_peak2_to_peak1 >= 0.90`
  - `peak12_distance_norm <= 0.25`
- basin quantile: `0.15`
- local random-walk estimator:
  - walks: `80`
  - max steps: `12`
  - fit range: `t=4..10`
- threshold band:
  - parsed from v1 metric threshold `(1.2,3.5)` (fallback defaults identical)

## Evaluation Blocks

Primary:

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`

Attack:

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3601..4100`

Holdout:

- datasets: `DS-004,DS-008`
- seeds: `3401..3600`

## Promotion Criteria

Mandatory:

1. `degraded_vs_v1 = 0` for `G18` on each block.
2. `degraded_vs_v1 = 0` for `QM_LANE` on each block.
3. per-dataset non-degradation for both scopes.

Primary uplift requirement:

4. explicit uplift on `DS-003` for `G18` (`improved > 0`).

Secondary:

5. net uplift (`improved > 0`) on evaluated block for both `G18` and `QM_LANE`.

## Tooling

Runner:

- `scripts/tools/run_qm_g18_candidate_eval_v2.py`

Evaluator:

- `scripts/tools/evaluate_qm_g18_promotion_v1.py`

## Output Package Targets

- `05_validation/evidence/artifacts/qm-g18-candidate-v2/`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/`
