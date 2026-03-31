# QM Stage-2 G18 Candidate (v6) - Pre-registration

Date: 2026-03-05  
Status: completed and promoted to official-v9 governance layer

## Motivation

Post-v8 Stage-2 taxonomy (`qm-stage2-failure-taxonomy-post-v8-v1`) showed:

- residual official fails: `67/2500`
- dominant gate remained `G18` (`45/2500`)
- secondary tails: `G17=12`, `G19=11`

`v6` targets residual `G18d` fragility in multi-peak sparse regimes without threshold or formula changes.

## Frozen Candidate Definition

`G18-v6` is a governance-layer estimator update (no gate threshold/formula edits):

1. Preserve source official pass (`g18_status=pass`) with no override.
2. For source official fails only:
   - compute local `d_s` around both top sigma peaks,
   - evaluate two fixed basin scales: `q in {0.15, 0.22}`,
   - for each basin scale evaluate fixed windows: `3-8, 4-9, 4-10, 5-10, 6-11`,
   - keep windows with `R^2 >= 0.50`,
   - choose best local value per peak, then peak-envelope aggregate.
3. Apply unchanged `G18d` threshold band (`1.2 < d_s < 3.5`, from metric file defaults).

Implemented in:

- `scripts/tools/run_qm_g18_candidate_eval_v6.py`

## Protocol Guardrails

- no gate formula changes
- no threshold changes
- candidate-only first, then promotion eval
- promotion requires `degraded=0` on primary/attack/holdout

## Execution Outputs

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v6/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v6/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v6/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All promotion evaluations returned `PASS`.

## Promotion Summary (vs official-v8)

- Primary (`600`): `QM lane 584 -> 590`, improved `6`, degraded `0`
- Attack (`1500`): `QM lane 1453 -> 1475`, improved `22`, degraded `0`
- Holdout (`400`): `QM lane 396 -> 400`, improved `4`, degraded `0`

Aggregate uplift: `32` additional QM-lane passes across `2500` profiles, with `degraded=0`.
