# Stability Baseline Guard (v1)

Purpose: freeze and guard the stability official-v2 policy outputs against regressions.

## Inputs

- official summaries:
  - `05_validation/evidence/artifacts/stability-official-v2/primary_s3401/summary.csv`
  - `05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401/summary.csv`
  - `05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401/summary.csv`

## Build Baselines

```bash
python scripts/tools/build_stability_baseline_v1.py --block primary
python scripts/tools/build_stability_baseline_v1.py --block attack
python scripts/tools/build_stability_baseline_v1.py --block holdout
```

Or:

```bash
make stability_baseline_build
```

## Run Guard

```bash
python scripts/tools/run_stability_regression_guard_v1.py
```

Or:

```bash
make stability_regression_guard
```

## Guard Fail Conditions

1. missing expected profile keys (`dataset_id, combo_id, case_id, case_seed`)
2. extra unexpected profiles
3. any official gate pass-rate drop vs baseline

## Main Outputs

- `05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check/block_summary.csv`
- `05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check/regression_report.json`
