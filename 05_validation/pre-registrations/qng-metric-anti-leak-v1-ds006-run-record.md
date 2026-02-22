# Run Record - QNG Metric Anti-Leak v1 on DS-006

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-004`
- Claim: `QNG-CORE-METRIC-V3-CONTROL`
- Base prereg lock: `05_validation/pre-registrations/qng-metric-anti-leak-v1.md`
- Policy: same controls, same threshold, no lock edits.

## Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_anti_leak_v1.py `
  --dataset-id DS-006 `
  --samples 72 `
  --seed 3401 `
  --rewire-runs 12 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds006"
```

## Result

- Decision: `pass`
- `label_perm_median=0.022733`
- `rewire_median=-0.119704`
- `rewire_shuffled_median=-0.033509`

