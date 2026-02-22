# Pre-Registration - QNG-T-TRJ-CTRL-001

- Date: 2026-02-21
- Test ID: `QNG-T-TRJ-CTRL-001`
- Scope: adversarial anti-shortcut controls for DS-005 trajectory signal

## Fixed Command

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

## Controls (Locked)

- `C1` orientation permutation on perigee science subset.
- `C2` segment-scale permutation on mixed science subset.
- `C3` sign-randomization collapse for directionality.
- `C4` symmetric/control rows near-zero sanity (`mean |a|/sigma`).

## Gates (Locked)

- `C1`: permutation `p <= 0.10` and ratio vs real `<= 0.45`.
- `C2`: permutation `p <= 0.10` and ratio vs real `<= 0.95`.
- `C3`: randomized directionality median `<= 0.60` and tail `p <= 0.10`.
- `C4`: control mean `|a|/sigma <= 1.50`.

## Stop Conditions

- No control-definition or threshold edits after execution.
- Any change requires `qng-t-trj-ctrl-001-v2.md`.

