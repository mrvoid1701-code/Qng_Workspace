# QM Stage-2 G18 Candidate (v5) - Pre-registration

Date: 2026-03-05  
Status: completed and promoted to official-v8 governance layer

## Motivation

Post-v7 Stage-2 taxonomy (`qm-stage2-failure-taxonomy-post-v7-v1`) shows:

- residual official fails: `121/2500`
- dominant gate remains `G18` (`99/2500`)
- `G17` and `G19` are secondary tails (`12` and `11`)

`v5` is reserved for the next `G18` estimator hardening step under the same anti post-hoc policy.

## Frozen Candidate Definition

`G18-v5` is a governance-layer estimator update (no gate threshold/formula edits):

1. Preserve source official pass (`g18_status=pass`) with no override.
2. For source official fails only:
   - recompute local spectral dimension on two peak basins,
   - use fixed multi-window fit set: `3-8, 4-9, 4-10, 5-10, 6-11`,
   - keep windows with `R^2 >= 0.50`,
   - choose best per-peak local `d_s`, then peak-envelope `max(peak1, peak2)`.
3. Apply unchanged `G18d` threshold band from run metrics (default fallback `1.2 < d_s < 3.5`).

Implemented in:

- `scripts/tools/run_qm_g18_candidate_eval_v5.py`

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

## Execution Outputs

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v5/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v5/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v5/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All promotion evaluations returned `PASS`.

## Promotion Summary (vs official-v7)

- Primary (`600`): `QM lane 571 -> 584`, improved `13`, degraded `0`
- Attack (`1500`): `QM lane 1426 -> 1453`, improved `27`, degraded `0`
- Holdout (`400`): `QM lane 382 -> 396`, improved `14`, degraded `0`

Aggregate uplift: `54` additional QM-lane passes across `2500` profiles, with `degraded=0`.
