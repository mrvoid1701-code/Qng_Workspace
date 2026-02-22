# Run Record: QNG-C-086b3 Scaling Law v1 (2026-02-21)

- Prereg source: `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md`
- Lock status: unchanged
- Runner: `scripts/run_qng_t_041_c086b3_scaling.py`
- Dataset: `DS-005`
- Holdout IDs: `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`

## Execution

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_041_c086b3_scaling.py `
  --test-id QNG-T-041 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --holdout-pass-ids JUNO_1,BEPICOLOMBO_1,SOLAR_ORBITER_1 `
  --out-dir 05_validation/evidence/artifacts/qng-t-041-c086b3-scaling
```

## Outcome

- `holdout_status=fail`
- `n_holdout=3`
- `holdout_rmse_log=15.382645` (gate `<=1.25`, fail)
- `holdout_mae_log=12.883496` (gate `<=1.00`, fail)
- `holdout_median_ratio=1.178824e+08` (gate `[0.50,2.00]`, fail)

## Data Caveat

Holdout geometry rows were ingested from Horizons vectors. Residual anomaly
fields are provisional placeholders (`delta_v_obs=0.0`, `delta_v_sigma=1.0`)
pending published OD residual summaries for these passes.

## Artifacts

- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/holdout-predictions.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/scaling-model.md`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/run-log.txt`
