# Evidence - QNG-T-TAUMAP-001

- Priority: P2
- Claim: real-data tau-map stability and geometry-coupling check
- Pre-registration: `05_validation/pre-registrations/qng-t-taumap-001.md`
- Status: pass

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_taumap_001.py `
  --test-id QNG-T-TAUMAP-001 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --exclude-placeholder-holdout `
  --seed 20260221 `
  --n-permutations 5000 `
  --out-dir 05_validation/evidence/artifacts/qng-t-taumap-001
```

## Key Metrics

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `global_tau_median` | `0.002200` | info | pass |
| `mission_cv_median` | `3.455614` | `<= 4.0` | pass |
| `mission_sign_consistency` | `0.666667` | `>= 2/3` | pass |
| `geometry_pearson_abs` | `0.978480` | `>= 0.70` | pass |
| `geometry_perm_p` | `0.044000` | `<= 0.10` | pass |
| `control_to_science_ratio` | `0.000000` | `<= 0.25` | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-taumap-001/tau_event_map.csv`
- `05_validation/evidence/artifacts/qng-t-taumap-001/tau_mission_summary.csv`
- `05_validation/evidence/artifacts/qng-t-taumap-001/geometry_coupling.csv`
- `05_validation/evidence/artifacts/qng-t-taumap-001/negative_controls.csv`
- `05_validation/evidence/artifacts/qng-t-taumap-001/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-taumap-001/run-log.txt`

## Decision

- Decision: pass
- Rationale: all locked tau-map gates passed on published DS-005 rows (placeholder holdout rows excluded).

