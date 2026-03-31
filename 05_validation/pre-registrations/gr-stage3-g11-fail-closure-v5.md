# Pre-registration: GR Stage-3 G11 Fail-Closure Candidate v5

Date: 2026-03-04  
Status: prereg only (candidate lane; no official switch)

## Objective

Address the residual `3/600` Stage-3 official fails (`G11` only) without threshold tuning.

## Frozen Inputs

Baseline reference:

- `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv`

Failure taxonomy reference:

- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/`

## Candidate Scope

Only `G11` decision estimator logic may be adjusted in candidate lane.

Non-negotiable constraints:

1. no changes to physics formulas,
2. no threshold relaxation,
3. no edits to `G12`, `G7`, `G8`, `G9` decision logic.

## Evaluation Blocks

1. Primary:
- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`

2. Attack:
- datasets: `DS-002,DS-003,DS-006`
- seeds: `3601..4100`

3. Holdout:
- datasets: `DS-004,DS-008`
- seeds: `3401..3600`

## Promotion Rule

Candidate v5 is promotion-eligible only if all are true:

1. `degraded=0` vs current official policy across all three blocks,
2. net improvement on primary (`improved > 0`),
3. residual fail signatures (`slope_instability`, `weak_corr_multi_peak`, `weak_corr_sparse_graph`) reduced or unchanged with no new fail class introduced,
4. Stage-3 baseline guard remains `PASS`.

## Deliverables

1. candidate summary packages (primary/attack/holdout),
2. promotion evaluator report (`report.md` + `report.json`),
3. strict fail taxonomy rerun on candidate outputs,
4. governance switch document only if promotion rule passes.

