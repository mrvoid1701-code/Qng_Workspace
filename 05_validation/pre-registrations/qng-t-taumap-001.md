# Pre-Registration - QNG-T-TAUMAP-001

- Date: 2026-02-21
- Test ID: `QNG-T-TAUMAP-001`
- Scope: real-data tau map on DS-005 flyby residual rows with locked geometry-coupling and control-separation gates

## Fixed Command

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

## Locked Inputs

- `data/trajectory/flyby_ds005_real.csv`
- Placeholder-holdout rows excluded (`notes/source_ref contains "placeholder"`).

## Gates (Locked)

- `G1 mission stability`: median mission-level `tau_cv <= 4.0` on missions with repeated science events.
- `G2 sign transferability`: mission sign-consistency vs global median tau `>= 2/3`.
- `G3 geometry coupling`: Pearson correlation between `|a_obs|` and `|x_feature|` `>= 0.70` and permutation `p <= 0.10`.
- `G4 control separation`: median `|tau|` on controls `<= 0.25 *` median `|tau|` on science rows.

## Stop Conditions

- Threshold edits are not allowed post-run.
- Any gate change requires `qng-t-taumap-001-v2.md`.

