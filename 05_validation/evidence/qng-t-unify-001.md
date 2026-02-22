# Evidence - QNG-T-UNIFY-001

- Priority: P2
- Claim: one-parameter global memory law across lensing + rotation
- Pre-registration: `05_validation/pre-registrations/qng-t-unify-001.md`
- Status: pass

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_unify_hysteresis_001.py `
  --test-id-unify QNG-T-UNIFY-001 `
  --test-id-hyst QNG-T-HYST-001 `
  --dataset-id DS-006 `
  --lensing-csv data/lensing/lensing_ds006_hybrid.csv `
  --rotation-csv data/rotation/rotation_ds006_rotmod.csv `
  --out-dir 05_validation/evidence/artifacts/qng-t-unify-001
```

## Key Metrics

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `lambda_global` | `1.000000` | locked one-parameter fit | pass |
| `delta_chi2_one_vs_base` | `-8.809870e+05` | `< 0` | pass |
| `delta_aic_one_vs_base` | `-8.809850e+05` | `<= -10` | pass |
| `delta_bic_one_vs_base` | `-8.809788e+05` | `<= -10` | pass |
| `delta_aic_one_vs_two` | `-1.999989` | `<= 2.5` | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-unify-001/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/one_parameter_comparison.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/hysteresis_summary.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/subset_assignments.csv`
- `05_validation/evidence/artifacts/qng-t-unify-001/run-summary.md`
- `05_validation/evidence/artifacts/qng-t-unify-001/run-log.txt`

## Decision

- Decision: pass
- Rationale: one locked global parameter explains both lensing and rotation with strong AIC/BIC support and remains competitive vs two-parameter reference.

