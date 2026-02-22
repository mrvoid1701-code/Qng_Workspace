# Evidence - QNG-T-HYST-001

- Priority: P2
- Claim: temporal-hysteresis style subset contrast without new parameters
- Pre-registration: `05_validation/pre-registrations/qng-t-hyst-001.md`
- Status: pass

## Run Link

This test uses the same locked run as `QNG-T-UNIFY-001`:

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

## Key Metrics

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `relaxed_obs_median` | `0.296762` | info | pass |
| `merging_obs_median` | `2.089370` | `merging > relaxed` | pass |
| `relaxed_pred_median` | `0.296762` | info | pass |
| `merging_pred_median` | `2.089370` | `merging > relaxed` | pass |
| `dispersion_ratio_obs` | `2.376508` | info | pass |
| `dispersion_ratio_pred` | `2.376508` | info | pass |
| `dispersion_alignment_log` | `0.000000` | `<= 0.20` | pass |
| `no_new_params` | `True` | required | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-unify-001/hysteresis_summary.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/subset_assignments.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/fit-summary.csv`

## Decision

- Decision: pass
- Rationale: high-offset (merging-like) vs low-offset (relaxed-like) contrast is reproduced by the same locked global parameter from the unify test, with no additional fitted parameters.

