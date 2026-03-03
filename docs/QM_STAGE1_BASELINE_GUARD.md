# QM Stage-1 Baseline + Regression Guard (v1)

This document defines the QM Stage-1 baseline/guard workflow, analogous to GR baseline guards.

## Scope

- Lane: QM Stage-1 official (`qm-stage1-g18-v2-official`)
- Blocks:
  - primary (`DS-002/003/006`, seeds `3401..3600`)
  - attack (`DS-002/003/006`, seeds `3601..4100`)
  - holdout (`DS-004/008`, seeds `3401..3600`)

## Baseline Inputs

- Official summaries:
  - `05_validation/evidence/artifacts/qm-stage1-official-v3/*/summary.csv`
- Promotion artifacts:
  - `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/*/report.json`
- Numeric metric source summaries (for descriptive min/median/p95 stats):
  - `05_validation/evidence/artifacts/qm-g18-candidate-v2/*/summary.csv`

## Build Baselines

One command:

```bash
make qm_stage1_baseline_build
```

Equivalent direct builder calls:

```bash
python scripts/tools/build_qm_stage1_baseline_v1.py --block primary
python scripts/tools/build_qm_stage1_baseline_v1.py --block attack
python scripts/tools/build_qm_stage1_baseline_v1.py --block holdout
```

Generated baseline JSONs:

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json`

Each baseline stores:

- profile set (`dataset_id`, `seed`)
- pass-rate snapshots for official gates (`G17/G18/G19/G20/QM lane`) and subgates (`G17a/b/c/d`)
- numeric metric stats (`min`, `median`, `p95`) for available numeric fields
- promotion decision metadata (`report.json` snapshot)

## Run Regression Guard

One command:

```bash
make qm_stage1_regression_guard
```

Equivalent direct guard call:

```bash
python scripts/tools/run_qm_stage1_regression_guard_v1.py --out-dir 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check
```

## Guard Decision Rules

Guard returns `FAIL` if any of the following is true:

1. any expected `(dataset_id, seed)` profile is missing
2. any extra `(dataset_id, seed)` profile appears
3. any official gate pass-rate decreases vs baseline

Guard returns `PASS` only if all three blocks (`primary`, `attack`, `holdout`) pass.

## Guard Outputs

Under:

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/`

Files:

- `block_summary.csv`
- `pass_rate_checks.csv`
- `profile_diffs.csv`
- `status_mismatches.csv`
- `regression_report.md`
- `regression_report.json`

Interpretation:

- `decision=PASS`: no pass-rate degradation and no profile-set drift.
- `decision=FAIL`: inspect `profile_diffs.csv` first, then `pass_rate_checks.csv` for degraded official fields.
