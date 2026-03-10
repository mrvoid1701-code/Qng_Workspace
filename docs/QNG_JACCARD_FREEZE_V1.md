# QNG Jaccard Freeze v1

This package freezes the current operational Jaccard lane (G10..G21).

## Commands

```bash
make qng_jaccard_freeze_v1
make qng_jaccard_regression_guard_v1
```

## Outputs

Freeze package:
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/gate_status_snapshot.csv`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/metric_snapshot.csv`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/summary.json`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/manifest.json`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/report.md`

Guard report:
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/latest_check/checks.csv`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/latest_check/details.csv`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/latest_check/regression_report.json`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/latest_check/regression_report.md`

## Guard logic

The guard fails when any of the following happens relative to freeze baseline:
- missing or extra gates
- missing or extra subgate metrics
- gate degradation (`pass -> fail`)
- subgate degradation (`pass -> fail`)
