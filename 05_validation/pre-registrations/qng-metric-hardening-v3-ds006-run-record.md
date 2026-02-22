# Run Record - QNG Metric Hardening v3 on DS-006

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-003`
- Claim: `QNG-CORE-METRIC-V3`
- Base prereg lock: `05_validation/pre-registrations/qng-metric-hardening-v3.md`
- Method lock: `01_notes/metric/metric-lock-v3.md`
- Policy: same lock, same gates, no threshold changes.

## Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py `
  --dataset-id DS-006 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 3401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006"
```

## Result

- Decision: `pass`
- Gate summary:
  - `D1 min_eig_global = 0.300471` (pass)
  - `D2 median_delta_g = 0.059885`, `p90_delta_g = 0.139852` (pass)
  - `D3 median_cos_sim = 0.995345`, `p10_cos_sim = 0.959466` (pass)
  - `D4 median_cos_sim_shuffled = -0.430659` (pass)

## Artifacts

- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/metric_checks.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/eigs.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/drift.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/align_sigma.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/config.json`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/run-log.txt`

