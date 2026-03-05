# QM Stage-2 G18 Candidate (v5) - Pre-registration

Date: 2026-03-05  
Status: draft candidate-only lane (next iteration)

## Motivation

Post-v7 Stage-2 taxonomy (`qm-stage2-failure-taxonomy-post-v7-v1`) shows:

- residual official fails: `121/2500`
- dominant gate remains `G18` (`99/2500`)
- `G17` and `G19` are secondary tails (`12` and `11`)

`v5` is reserved for the next `G18` estimator hardening step under the same anti post-hoc policy.

## Frozen Inputs

- Stage-2 raw summaries:
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/*/qm_lane/summary.csv`
- Official-v7 reference:
  - `05_validation/evidence/artifacts/qm-stage1-official-v7/*/summary.csv`
- Post-v7 taxonomy:
  - `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v7-v1/`

## Protocol Guardrails

- no gate formula changes
- no threshold changes
- candidate-only first, then promotion eval
- promotion requires `degraded=0` on primary/attack/holdout

## TODO Before Execution

1. Freeze exact `G18-v5` estimator definition.
2. Freeze evaluation command set and output directories.
3. Run primary/attack/holdout promotion checks.
4. Apply official switch only in a separate governance commit if all criteria pass.
