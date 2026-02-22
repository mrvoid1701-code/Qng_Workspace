# Evidence - QNG-T-GEODESIC-001

- Priority: P3
- Claim: metric-v3 trajectories are numerically stable and Newtonian-compatible
- Pre-registration: `05_validation/pre-registrations/qng-t-geodesic-001.md`
- Status: pass

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_geodesic_001.py `
  --test-id QNG-T-GEODESIC-001 `
  --dataset-ids DS-002,DS-003,DS-006 `
  --samples 72 `
  --seed 3401 `
  --steps 40 `
  --dt 0.05 `
  --out-dir 05_validation/evidence/artifacts/qng-t-geodesic-001
```

## Cross-Dataset Metrics

| Dataset | stable_fraction | cos_median / cos_p10 | mag_ratio_median / p90 | Status |
| --- | --- | --- | --- | --- |
| DS-002 | `1.000000` | `0.995563 / 0.960162` | `1.918975 / 2.443143` | pass |
| DS-003 | `1.000000` | `0.993609 / 0.965849` | `2.012932 / 2.646473` | pass |
| DS-006 | `1.000000` | `0.995936 / 0.955608` | `1.989548 / 2.458627` | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-geodesic-001/trajectory_samples.csv`
- `05_validation/evidence/artifacts/qng-t-geodesic-001/dataset_summary.csv`
- `05_validation/evidence/artifacts/qng-t-geodesic-001/checks.csv`
- `05_validation/evidence/artifacts/qng-t-geodesic-001/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-geodesic-001/geodesic-report.md`
- `05_validation/evidence/artifacts/qng-t-geodesic-001/run-log.txt`

## Decision

- Decision: pass
- Rationale: all locked geodesic sanity gates (`G1..G3`) pass on DS-002/003/006.

