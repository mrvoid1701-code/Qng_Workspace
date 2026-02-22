# Evidence - QNG-T-GRSWEEP-001

- Priority: P3
- Claim: `tau -> 0` kill-switch should recover GR-like baseline behavior
- Pre-registration: `05_validation/pre-registrations/qng-t-grsweep-001.md`
- Status: pass

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_grsweep_001.py `
  --test-id QNG-T-GRSWEEP-001 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --use-pioneer-anchor `
  --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv `
  --n-steps 10 `
  --out-dir 05_validation/evidence/artifacts/qng-t-grsweep-001
```

## Key Metrics

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `tau_hat` | `1.368655e-04` | info | pass |
| `delta_chi2_science(alpha=1-0)` | `-5849.293279` | `<= -1000` | pass |
| `delta_chi2_control(alpha=1-0)` | `-1.242299` | ratio gate | pass |
| `control_delta_ratio_vs_science` | `2.123845e-04` | `<= 0.05` | pass |
| monotonic science activation | `True` | required | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-grsweep-001/tau_sweep.csv`
- `05_validation/evidence/artifacts/qng-t-grsweep-001/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-grsweep-001/gr-killswitch-report.md`
- `05_validation/evidence/artifacts/qng-t-grsweep-001/run-log.txt`

## Decision

- Decision: pass
- Rationale: signal grows monotonically with tau while control response remains negligible.

