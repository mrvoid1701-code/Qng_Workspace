# QM Stage-1 Official Switch (G18-v5 policy)

Date: 2026-03-05

Effective tag: `qm-stage1-g18-v5-official`

## Summary

QM Stage-1 official policy is switched from `official-v7` to `official-v8` using `G18-v5` candidate outputs, with no gate formula or threshold changes.

## Promotion Evidence

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v5/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v5/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v5/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All three promotion evaluations returned `PASS` with `degraded=0`.

## Official-v8 Apply Outputs

- `05_validation/evidence/artifacts/qm-stage1-official-v8/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v8/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v8/attack_holdout_ds004_008_s3401_3600/`

Official readout vs `official-v7`:

- primary: `G18 579/600 -> 592/600`, `QM lane 571/600 -> 584/600`
- attack: `G18 1440/1500 -> 1467/1500`, `QM lane 1426/1500 -> 1453/1500`
- holdout: `G18 382/400 -> 396/400`, `QM lane 382/400 -> 396/400`

## Baseline + Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v6/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v6/latest_check/`
- guard decision: `PASS`

## Stage-2 Projection Update

Using Stage-2 raw summaries projected through `official-v8`:

- pass: `2433/2500` (up from `2379/2500` under `official-v7`)
- improved `fail->pass`: `683`
- degraded `pass->fail`: `0`

Residual dominant failing gate remains `G18` (`45/2500`), followed by `G17` (`12`) and `G19` (`11`).
