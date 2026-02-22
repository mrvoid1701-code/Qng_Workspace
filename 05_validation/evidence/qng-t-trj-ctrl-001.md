# Evidence - QNG-T-TRJ-CTRL-001

- Priority: P2
- Claim: trajectory signal survives adversarial anti-shortcut controls
- Pre-registration: `05_validation/pre-registrations/qng-t-trj-ctrl-001.md`
- Status: pass

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_trj_ctrl_001.py `
  --test-id QNG-T-TRJ-CTRL-001 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --use-pioneer-anchor `
  --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv `
  --n-runs 1200 `
  --seed 20260221 `
  --out-dir 05_validation/evidence/artifacts/qng-t-trj-ctrl-001
```

## Key Metrics

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `orientation_p_value` | `0.011667` | `<= 0.10` | pass |
| `orientation_ratio_vs_real` | `0.256489` | `<= 0.45` | pass |
| `segment_p_value` | `0.050833` | `<= 0.10` | pass |
| `segment_ratio_vs_real` | `0.842167` | `<= 0.95` | pass |
| `directionality_randomized_median` | `0.428571` | `<= 0.60` | pass |
| `directionality_tail_p` | `0.057500` | `<= 0.10` | pass |
| `control_mean_abs_over_sigma` | `0.400000` | `<= 1.50` | pass |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-trj-ctrl-001/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-trj-ctrl-001/anti_shortcut_summary.csv`
- `05_validation/evidence/artifacts/qng-t-trj-ctrl-001/anti_shortcut_report.md`
- `05_validation/evidence/artifacts/qng-t-trj-ctrl-001/run-log.txt`

## Decision

- Decision: pass
- Rationale: all locked anti-shortcut gates (`C1..C4`) passed under adversarial trajectory controls.

