# QM Stage-2 G18 Candidate (v4) - Pre-registration

Date: 2026-03-04  
Status: PROMOTED -> official policy as of 2026-03-05 (`qm-stage1-g18-v4-official`)

## Motivation

Post-v6 Stage-2 taxonomy (`qm-stage2-failure-taxonomy-post-v6-v1`) over `2500` joined profiles shows:

- residual official fails: `181/2500`
- dominant failing gate: `G18` (`160/2500`)
- `G17` reduced to `12/2500`, `G19` low (`11/2500`), `G20` stable (`0`)

This prereg isolates `G18` as the next candidate lane, keeping all thresholds/formulas in core runners unchanged.

## Frozen Inputs

- Stage-2 raw summaries:
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/*/qm_lane/summary.csv`
- Official-v6 reference summaries:
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/*/summary.csv`
- Post-v6 taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v6-v1/`
- Blocks:
  - primary: `DS-002/003/006`, seeds `3401..3600`
  - attack: `DS-002/003/006`, seeds `3601..4100`
  - holdout: `DS-004/008`, seeds `3401..3600`

## Candidate Scope

- Modify only candidate mapping/estimator logic for `G18` evaluation lane.
- Keep `G17/G19/G20` decisions inherited and unchanged.
- No edits to physics formulas in gate runners.
- No threshold tuning.

## Frozen Evaluation Protocol

For each block (primary/attack/holdout):

1. Run candidate evaluation summary with `G18-v4`.
2. Compare candidate vs official-v6 baseline by `(dataset, seed)`.
3. Emit transition report:
   - improved (`fail->pass`)
   - degraded (`pass->fail`)
   - per-dataset deltas

## Promotion Criteria (must all hold)

1. `degraded=0` per block.
2. Net uplift on primary.
3. Net uplift on attack.
4. Holdout non-degradation mandatory.
5. Dominant residual fail count on `G18` decreases materially vs post-v6 baseline (`160`).
6. Coupling stability remains unchanged (`G20` and GR guard expectations unaffected).

## Governance Rule

- If all criteria pass: open separate governance switch proposal.
- If not: keep candidate-only, publish fail taxonomy delta.

## Anti Post-Hoc Guard

- No threshold edits after observing results.
- Any estimator-definition change requires prereg revision (`v5`).

## Completion Snapshot (2026-03-05)

Evaluation outputs:

- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

Readout:

- primary: `PASS`, improved `+28` on `G18`, degraded `0`
- attack: `PASS`, improved `+101` on `G18`, degraded `0`
- holdout: `PASS`, improved `+22` on `G18`, degraded `0`

Governance apply:

- `05_validation/evidence/artifacts/qm-stage1-official-v7/*`
- switch note: `docs/QM_STAGE1_G18_V4_OFFICIAL_SWITCH.md`
