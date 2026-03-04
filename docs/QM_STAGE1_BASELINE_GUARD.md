# QM Stage-1 Baseline + Regression Guard (v4)

This document defines the current QM Stage-1 baseline/guard workflow after the `G17b-v4` official switch.

## Scope

- Lane: QM Stage-1 official (`qm-stage1-g17b-v4-official`)
- Blocks:
  - primary (`DS-002/003/006`, seeds `3401..3600`)
  - attack (`DS-002/003/006`, seeds `3601..4100`)
  - holdout (`DS-004/008`, seeds `3401..3600`)

## Baseline Inputs

- Official summaries:
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/*/summary.csv`
- Promotion reports:
  - `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/*/report.json`
- Numeric metrics summaries:
  - `05_validation/evidence/artifacts/qm-g17b-candidate-v4/*/summary.csv`

## Build Baselines

```bash
python scripts/tools/build_qm_stage1_baseline_v1.py --block primary --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/primary_ds002_003_006_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17b-candidate-v4/primary_ds002_003_006_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_primary.json --baseline-id qm-stage1-baseline-primary-v4 --effective-tag qm-stage1-g17b-v4-official
python scripts/tools/build_qm_stage1_baseline_v1.py --block attack --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/attack_seed500_ds002_003_006_s3601_4100/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17b-candidate-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_attack.json --baseline-id qm-stage1-baseline-attack-v4 --effective-tag qm-stage1-g17b-v4-official
python scripts/tools/build_qm_stage1_baseline_v1.py --block holdout --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17b-candidate-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_holdout.json --baseline-id qm-stage1-baseline-holdout-v4 --effective-tag qm-stage1-g17b-v4-official
```

Generated baseline JSON files:

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_primary.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_attack.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_holdout.json`

Each baseline stores:

- expected profile set (`dataset_id`, `seed`)
- pass-rate snapshot for official gates and key subgates
- numeric metric stats (`min`, `median`, `p95`) where available
- promotion metadata snapshot

## Run Regression Guard

```bash
python scripts/tools/run_qm_stage1_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/qm_stage1_baseline_holdout.json --summary-primary-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/primary_ds002_003_006_s3401_3600/summary.csv --summary-attack-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/attack_seed500_ds002_003_006_s3601_4100/summary.csv --summary-holdout-csv 05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check
```

## Guard Decision Rules

Guard returns `FAIL` if any of the following happens:

1. missing expected `(dataset_id, seed)` profiles
2. extra unexpected `(dataset_id, seed)` profiles
3. any official gate pass-rate decreases vs baseline

Guard returns `PASS` only if all three blocks pass.

## Guard Outputs

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/block_summary.csv`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/pass_rate_checks.csv`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/profile_diffs.csv`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/status_mismatches.csv`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/latest_check/regression_report.json`
