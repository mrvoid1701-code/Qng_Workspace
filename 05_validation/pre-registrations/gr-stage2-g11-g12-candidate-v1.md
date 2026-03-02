# GR Stage-2 G11/G12 Candidate Plan (v1, Pre-Registered)

Date: 2026-03-02  
Status: candidate-only plan (no official gate switch)

## Scope

Target only Stage-2 weak points identified in taxonomy:

- `G11` fails: `19/600` (dominant signature: `G11a`)
- `G12` fails: `15/600` (dominant signature: `G12d`)

Source package:

- `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/`

## Frozen Governance

1. Keep `G11/G12 v1` unchanged as official Stage-2 baseline.
2. Add `v2` as candidate-only diagnostics.
3. No edits to `run_qng_einstein_eq_v1.py` or `run_qng_gr_solutions_v1.py` in this phase.

## Candidate Definitions (for evaluation only)

### G11a-v2-candidate

Purpose: reduce sensitivity to borderline OLS linear-fit behavior.

Definition:

- compute Spearman rank correlation between `R` and `rho` from `einstein_eq.csv`
- candidate decision:
  - pass if `G11a-v1` is pass, OR
  - pass if (`G11b-v1`, `G11c-v1`, `G11d-v1` are pass) AND `spearman(R,rho) >= 0.20`

Note:

- `0.20` is reused from existing prereg correlation floor used in `G16b` candidate lane (not tuned on this run).

### G12d-v2-candidate

Purpose: reduce radial-fit instability from edge bins.

Definition:

- compute robust/trimmed slope on `log|R_bin_mean|` vs `log(r_bin)` using mid radial bins only
- keep same decision threshold as v1:
  - pass if slope `< -0.03`

Note:

- threshold is unchanged; only estimator is candidate.

## Evaluation Grid (Frozen)

Primary grid:

- datasets: `DS-002, DS-003, DS-006`
- seeds: `3401..3600`
- `phi_scale=0.08`

Attack A:

- same datasets
- seeds: `3601..4100`

Attack B:

- holdout datasets: `DS-004, DS-008`
- seeds: `3401..3600`

## Promotion Criteria (must all pass)

For each target gate (`G11`, `G12`):

1. `degraded_vs_v1 = 0` on primary grid.
2. Per-dataset non-degradation on primary grid.
3. Global fail-count reduction vs v1 on primary grid.
4. Attack A and Attack B must satisfy non-degradation.

Gate switch policy:

- if all criteria pass: promote candidate to official for next Stage-2 release point.
- else: keep v1 official; keep v2 candidate-only.

## Execution Record (2026-03-02)

Evaluations were executed on:

1. primary grid: `DS-002/003/006`, `3401..3600`
2. attack A: `DS-002/003/006`, `3601..4100`
3. attack B: `DS-004/008`, `3401..3600`

Outcome summary:

- `G12-v2`: passed all criteria in primary + both attacks.
- `G11-v2`: failed uplift criterion in all runs (no recovered fail-cases).
- combined `G11+G12` promotion package: not eligible for official switch.

Decision file:

- `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/promotion_decision.md`
