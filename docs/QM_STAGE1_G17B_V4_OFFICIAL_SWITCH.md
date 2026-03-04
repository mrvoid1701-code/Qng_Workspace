# QM Stage-1 Official Switch (G17b-v4 policy)

Date: 2026-03-04

Effective tag: `qm-stage1-g17b-v4-official`

## Summary

QM Stage-1 official policy is switched from `official-v5` to `official-v6` using `G17b-v4` candidate outputs, with no gate formula or threshold changes.

## Promotion Evidence

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g17b-candidate-v4/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g17b-candidate-v4/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g17b-candidate-v4/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All three promotion evaluations returned `PASS` with `degraded=0`.

## Official-v6 Apply Outputs

- `05_validation/evidence/artifacts/qm-stage1-official-v6/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/`

Readout:

- primary: `G17 564/600 -> 596/600`, `QM lane 529/600 -> 560/600`
- attack: `G17 1416/1500 -> 1492/1500`, `QM lane 1316/1500 -> 1387/1500`
- holdout: unchanged with non-degradation (`400/400` for `G17`, `372/400` for lane)

## Baseline + Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/`
- guard decision: `PASS`

## Runtime Note

Session tracking note (requested): this full switch package was recorded as a `~5h` process window including candidate generation, promotion checks, official apply, and baseline/guard refresh.
