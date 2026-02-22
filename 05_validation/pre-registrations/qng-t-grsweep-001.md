# Pre-Registration - QNG-T-GRSWEEP-001

- Date: 2026-02-21
- Test ID: `QNG-T-GRSWEEP-001`
- Scope: hard GR kill-switch by sweeping `tau` from `0` to fitted `tau_hat`

## Fixed Command

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

## Gates (Locked)

- `S1`: monotonic science activation: `chi2_science(alpha_i)` non-increasing for `alpha in [0,1]`.
- `S2`: endpoint signal strength: `delta_chi2_science(alpha=1 - alpha=0) <= -1000`.
- `S3`: control cleanliness: `|delta_chi2_control| / |delta_chi2_science| <= 0.05`.

## Stop Conditions

- No gate edits after execution.
- Any threshold change requires `qng-t-grsweep-001-v2.md`.

