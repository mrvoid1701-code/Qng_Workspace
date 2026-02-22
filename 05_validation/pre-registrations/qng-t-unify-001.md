# Pre-Registration - QNG-T-UNIFY-001

- Date: 2026-02-21
- Test ID: `QNG-T-UNIFY-001`
- Scope: one-parameter global memory law across lensing + rotation under same sample/likelihood settings

## Fixed Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_unify_hysteresis_001.py `
  --test-id-unify QNG-T-UNIFY-001 `
  --test-id-hyst QNG-T-HYST-001 `
  --dataset-id DS-006 `
  --lensing-csv data/lensing/lensing_ds006_hybrid.csv `
  --rotation-csv data/rotation/rotation_ds006_rotmod.csv `
  --out-dir 05_validation/evidence/artifacts/qng-t-unify-001
```

## Locked Inputs

- `data/lensing/lensing_ds006_hybrid.csv`
- `data/rotation/rotation_ds006_rotmod.csv`
- single global parameter: `lambda`

## Gates (Locked)

- `U1`: `delta_chi2_one_vs_base < 0`
- `U2`: `delta_aic_one_vs_base <= -10`
- `U3`: `delta_bic_one_vs_base <= -10`
- `U4`: one-parameter competitiveness vs two-parameter reference: `delta_aic_one_vs_two <= 2.5`

## Stop Conditions

- No sample/noise/likelihood changes after run.
- Any gate change requires `qng-t-unify-001-v2.md`.

