# QM Stage-1 Official Switch (G18-v4 policy)

Date: 2026-03-05

Effective tag: `qm-stage1-g18-v4-official`

## Summary

QM Stage-1 official policy is switched from `official-v6` to `official-v7` using `G18-v4` candidate outputs, with no gate formula or threshold changes.

## Promotion Evidence

Candidate outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v4/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v4/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v4/attack_holdout_ds004_008_s3401_3600/`

Promotion eval outputs:

- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

All three promotion evaluations returned `PASS` with `degraded=0`.

## Official-v7 Apply Outputs

- `05_validation/evidence/artifacts/qm-stage1-official-v7/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v7/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v7/attack_holdout_ds004_008_s3401_3600/`

Official readout vs `official-v6`:

- primary: `G18 568/600 -> 579/600`, `QM lane 560/600 -> 571/600`
- attack: `G18 1400/1500 -> 1440/1500`, `QM lane 1387/1500 -> 1426/1500`
- holdout: `G18 372/400 -> 382/400`, `QM lane 372/400 -> 382/400`

## Baseline + Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v5/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v5/latest_check/`
- guard decision: `PASS`

## Stage-2 Projection Update

Using Stage-2 raw summaries projected through `official-v7`:

- pass: `2379/2500` (up from `2319/2500` under `official-v6`)
- improved `fail->pass`: `629`
- degraded `pass->fail`: `0`

Residual dominant failing gate remains `G18` (`99/2500`), indicating next candidate work should stay focused on `G18`.
