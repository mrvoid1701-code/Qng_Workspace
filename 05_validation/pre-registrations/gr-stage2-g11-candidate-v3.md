# GR Stage-2 G11a Candidate Plan (v3, Pre-Registered)

Date: 2026-03-02  
Status: candidate-only plan (no official switch in this step)

## Scope

Target only the remaining Stage-2 official weak point:

- source summary: `05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv`
- `G11` fails: `13/600`
- dominant signature from strict fail taxonomy:
  - weak high-signal correlation (`12/13`)
  - low-signal and multi-peak subsets are frequent co-factors

Reference taxonomy package:

- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2/`

## Frozen Governance

1. Keep official Stage-2 policy unchanged (`G11a-v2 + G12d-v2`).
2. Add `G11a-v3` as candidate-only.
3. No edits to:
   - `scripts/run_qng_einstein_eq_v1.py`
   - `scripts/tools/run_gr_stage2_official_v2.py`

## Candidate Definition (G11a-v3, evaluation only)

Physics-motivated estimator hardening:

1. Keep `R(i)` from existing Einstein-equation runner (no curvature change).
2. Build source proxy from sigma via Poisson-like discrete operator:
   - `S(i) = |L_rw sigma_norm(i)|`
3. Smooth curvature once on graph:
   - `R_smooth(i) = 0.5 * R(i) + 0.5 * mean_{j in N(i)} R(j)`
4. Compare `S` vs `|R_smooth|` on high-signal subset (`top 20% S`).
5. Fallback pass condition (for `G11a-v3`) requires:
   - `G11b/G11c/G11d` pass
   - `|Spearman(S, |R_smooth|)| >= 0.20`
   - `|Pearson(S, |R_smooth|)| >= 0.20`

Constants (frozen):

- high-signal quantile: `0.80`
- correlation floor: `0.20`
- smoothing: one iteration, `alpha=0.50`

Multi-peak / G11b-fail branch:

- computed as diagnostic-only fields in v3 output
- does not override decision in this prereg step

## Evaluation Grid (Frozen)

Primary:

- datasets: `DS-002, DS-003, DS-006`
- seeds: `3401..3600`

Attack A:

- datasets: `DS-002, DS-003, DS-006`
- seeds: `3601..4100`

Attack B (holdout):

- datasets: `DS-004, DS-008`
- seeds: `3401..3600`

## Promotion Criteria

Primary criteria:

1. `degraded_vs_v2 = 0`
2. `improved_vs_v2 >= 5`
3. per-dataset non-degradation
4. weak-corr fail-count drop `>= 2`

Attack criteria:

1. `degraded_vs_v2 = 0`
2. `improved_vs_v2 >= 1`
3. weak-corr fail-count drop `>= 1` (holdout may use `>=0` if fail count is very small)

Decision rule:

- only if primary + both attacks satisfy checks, candidate is promotion-ready.
- otherwise keep current official policy unchanged.

## Execution Record (2026-03-02)

Evaluations executed:

1. primary (`DS-002/003/006`, `3401..3600`)
2. attack A (`DS-002/003/006`, `3601..4100`)
3. holdout (`DS-004/008`, `3401..3600`)

Observed outcomes:

- primary: `587/600 -> 594/600`, improved `7`, degraded `0`, weak-corr drop `7`
- attack A: `1451/1500 -> 1464/1500`, improved `13`, degraded `0`, weak-corr drop `12`
- holdout: `394/400 -> 398/400`, improved `4`, degraded `0`, weak-corr drop `4`

Decision file:

- `05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/promotion_decision.md`
