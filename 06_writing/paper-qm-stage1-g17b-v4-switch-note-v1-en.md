# QM Stage-1 G17b-v4 Official Switch Note (v1)

Date: 2026-03-04

## Abstract

This note documents a governance-layer QM Stage-1 update in QNG where `G17b-v4` is promoted and applied as the official decision policy (`official-v6`) without changing physical formulas or gate thresholds. The change targets known `G17b` fragility by using a high-signal slope recovery rule only on legacy fail cases, while preserving legacy pass cases and enforcing non-degradation.

## Frozen Candidate Definition

- Input lane: frozen `qm-stage1-official-v5` profile summaries.
- Rule:
  - keep `G17b-v1` pass decisions unchanged;
  - for `G17b-v1` fail cases, compute high-signal OLS slope on top-`q=0.80` by `|G_ij|`;
  - require support `n_used >= 80`;
  - apply unchanged legacy threshold (`slope < -0.01`).
- No gate formula edits and no threshold tuning.

## Evaluation Protocol

Three prereg blocks were evaluated:

- primary: `DS-002/003/006`, seeds `3401..3600` (`n=600`)
- attack: `DS-002/003/006`, seeds `3601..4100` (`n=1500`)
- holdout: `DS-004/008`, seeds `3401..3600` (`n=400`)

Promotion criteria:

- degraded `= 0`
- per-dataset non-degradation
- net uplift required on primary/attack
- holdout allowed non-degrading no-uplift outcome

## Results

Primary:

- `G17: 564/600 -> 596/600` (`+32`, degraded `0`)
- `QM lane: 529/600 -> 560/600` (`+31`, degraded `0`)

Attack:

- `G17: 1416/1500 -> 1492/1500` (`+76`, degraded `0`)
- `QM lane: 1316/1500 -> 1387/1500` (`+71`, degraded `0`)

Holdout:

- `G17: 400/400 -> 400/400` (degraded `0`)
- `QM lane: 372/400 -> 372/400` (degraded `0`)

All promotion evaluations returned `PASS`.

## Official Apply and Regression Guard

Official mapping was applied to:

- `05_validation/evidence/artifacts/qm-stage1-official-v6/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/`

Baseline/guard refresh:

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/`
- latest guard decision: `PASS`

## Conclusion

`G17b-v4` is promoted to official QM Stage-1 governance as a non-degrading improvement with strong uplift on primary and attack blocks and stable holdout behavior. The evidence package supports continuation toward QM Stage-2 candidate work under the same anti post-hoc workflow.

## Runtime Note

Requested tracking note: end-to-end package completion was recorded as an approximately `5h` process window.
