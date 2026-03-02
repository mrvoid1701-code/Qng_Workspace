# QM G17 Candidate-v2 Pre-Registration (Hybrid Local-Gap Policy)

Date: 2026-03-02  
Status: candidate-only (does not replace G17-v1 by default)

## Why This Candidate Exists

DS-003 mini-sprint diagnosis (`3401..3430`) showed systematic G17 failures concentrated in `G17a` only:

- `G17 pass=20/30`, `fail=10/30`
- component split: `G17a fail=10`, `G17b/c/d fail=0`
- dominant fail class: `multipeak_mode_mixing`

Source package:

- `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/`

## Candidate Definition (Hybrid)

Baseline remains frozen:

- `G17-v1` logic and thresholds unchanged

Candidate update:

1. If `G17a-v1` is `pass`, keep `G17a-v2=pass` (accept-v1-pass guard).
2. If `G17a-v1` is `fail`:
   - detect multi-peak mixing using frozen diagnostics:
     - `sigma_peak2_to_peak1 >= 0.90`
     - `peak12_distance_norm <= 0.25`
   - if mixing=true, compute `local_gap` on primary basin subgraph (`top 15% sigma`, largest connected component).
   - apply same gap threshold as v1:
     - `local_gap > 0.01` -> `G17a-v2=pass`
     - else `fail`.
3. `G17b/G17c/G17d` are unchanged and reused from v1 outputs.
4. `G17-v2` is pass only if `G17a-v2 & G17b & G17c & G17d`.

No threshold tuning in core runner scripts is allowed.

## Runner / Evaluator

Runner:

- `scripts/tools/run_qm_g17_candidate_eval_v2.py`

Evaluator:

- `scripts/tools/evaluate_qm_g17_promotion_v1.py`

## Frozen Evaluation Blocks

Primary:

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`

Attack A:

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3601..4100`

Attack B holdout:

- datasets: `DS-004,DS-008`
- seeds: `3401..3600`

## Promotion Criteria

Mandatory:

1. `degraded_vs_v1 = 0` for `G17`.
2. `degraded_vs_v1 = 0` for `QM_LANE`.
3. per-dataset non-degradation for both scopes.

Primary uplift:

4. `improved_vs_v1 > 0` on primary for `G17`.
5. `improved_vs_v1 > 0` on primary for `QM_LANE` (if applicable).
