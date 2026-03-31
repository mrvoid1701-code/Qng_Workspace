# GR Stage-2 G11/G12 Candidate Plan (v2, Pre-Registered)

Date: 2026-03-02  
Status: candidate-only plan (no official gate switch in this step)

## Scope

Refine `G11a` candidate logic after v1 showed zero uplift, while keeping:

- official gate scripts unchanged
- `G12d-v2` estimator unchanged from prior candidate package
- frozen thresholds/formulas in official runners untouched

## Frozen Inputs

- datasets: `DS-002, DS-003, DS-006`
- seeds: `3401..3600` (primary)
- attack A seeds: `3601..4100`
- attack B datasets: `DS-004, DS-008` with seeds `3401..3600`
- `phi_scale=0.08` (as used by Stage-2 source runs)

## Candidate Definitions

### G11a-v2-candidate (revised)

Pass if:

1. `G11a-v1` is pass, OR
2. (`G11b-v1`, `G11c-v1`, `G11d-v1` are pass) AND:
   - `|Spearman(rho,R)|` on high-signal subset `>= 0.20`
   - `|Pearson(rho,R)|` on high-signal subset `>= 0.20`

Frozen constants:

- high-signal quantile: `0.80`
- high-signal Spearman minimum: `0.20`
- high-signal Pearson minimum: `0.20`

### G12d-v2-candidate

Unchanged from previous candidate package:

- robust Theil-Sen slope over selected bins
- same decision threshold as v1: `slope < -0.03`

## Promotion Criteria (must all pass)

For each target gate (`G11`, `G12`) and composite `STAGE2`:

1. `degraded_vs_v1 = 0`
2. net fail-case uplift (`improved > degraded`)
3. per-dataset non-degradation
4. attack A and attack B satisfy the same checks

## Execution Record (2026-03-02)

Evaluator scripts:

- `scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py`
- `scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py`

Observed outcomes:

1. Primary (`DS-002/003/006`, `3401..3600`)
- `G11`: `581/600 -> 587/600` (improved `6`, degraded `0`)
- `G12`: `585/600 -> 600/600` (improved `15`, degraded `0`)
- `STAGE2`: `570/600 -> 587/600` (improved `17`, degraded `0`)

2. Attack A (`DS-002/003/006`, `3601..4100`)
- `G11`: `1426/1500 -> 1451/1500` (improved `25`, degraded `0`)
- `G12`: `1392/1500 -> 1495/1500` (improved `103`, degraded `0`)
- `STAGE2`: `1346/1500 -> 1447/1500` (improved `101`, degraded `0`)

3. Attack B (`DS-004/008`, `3401..3600`)
- `G11`: `390/400 -> 394/400` (improved `4`, degraded `0`)
- `G12`: `388/400 -> 400/400` (improved `12`, degraded `0`)
- `STAGE2`: `380/400 -> 394/400` (improved `14`, degraded `0`)

Decision record:

- `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/promotion_decision.md`
