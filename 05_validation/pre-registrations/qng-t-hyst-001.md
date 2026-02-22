# Pre-Registration - QNG-T-HYST-001

- Date: 2026-02-21
- Test ID: `QNG-T-HYST-001`
- Scope: hysteresis-style subset contrast (relaxed-like vs merging-like) with no new fitted parameters

## Fixed Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_unify_hysteresis_001.py `
  --test-id-unify QNG-T-UNIFY-001 `
  --test-id-hyst QNG-T-HYST-001 `
  --dataset-id DS-006 `
  --lensing-csv data/lensing/lensing_ds006_hybrid.csv `
  --rotation-csv data/rotation/rotation_ds006_rotmod.csv `
  --subset-fraction 0.25 `
  --out-dir 05_validation/evidence/artifacts/qng-t-unify-001
```

## Locked Definitions

- subset split by observed lensing offset quantiles:
  - bottom 25% = `relaxed_like`
  - top 25% = `merging_like`
- prediction uses the same locked global `lambda` from `QNG-T-UNIFY-001` (no additional fit).

## Gates (Locked)

- `H1`: `median_obs(merging_like) > median_obs(relaxed_like)`
- `H2`: `median_pred(merging_like) > median_pred(relaxed_like)`
- `H3`: dispersion alignment `|log(disp_ratio_obs / disp_ratio_pred)| <= 0.20`
- `H4`: no new parameters introduced in hysteresis split evaluation

## Stop Conditions

- No post-hoc subset reshaping after seeing results.
- Any gate/split change requires `qng-t-hyst-001-v2.md`.

