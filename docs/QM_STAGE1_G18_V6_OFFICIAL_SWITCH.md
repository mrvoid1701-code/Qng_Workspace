# QM Stage-1 Official Switch (G18-v6 policy)

Date: 2026-03-05

Effective tag: `qm-stage1-g18-v6-official`

## Summary

QM Stage-1 official policy is switched from `official-v8` to `official-v9` using `G18-v6` candidate outputs, with no gate formula or threshold changes.

## Promotion Evidence

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v6/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v6/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v6/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All three promotion evaluations returned `PASS` with `degraded=0`.

## Official-v9 Apply Outputs

- `05_validation/evidence/artifacts/qm-stage1-official-v9/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v9/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v9/attack_holdout_ds004_008_s3401_3600/`

Official readout vs `official-v8`:

- primary: `G18 592/600 -> 598/600`, `QM lane 584/600 -> 590/600`
- attack: `G18 1467/1500 -> 1489/1500`, `QM lane 1453/1500 -> 1475/1500`
- holdout: `G18 396/400 -> 400/400`, `QM lane 396/400 -> 400/400`

## Baseline + Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v7/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v7/latest_check/`
- guard decision: `PASS`

## Stage-2 Projection Update

Using Stage-2 raw summaries projected through `official-v9`:

- pass: `2465/2500` (up from `2433/2500` under `official-v8`)
- improved `fail->pass`: `715`
- degraded `pass->fail`: `0`

Residual dominant failing gate remains `G18` (`12/2500`), followed by `G17` (`12`) and `G19` (`11`).
