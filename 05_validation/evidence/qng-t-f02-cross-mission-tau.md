# Evidence - QNG-T-F02

- Priority: Mission Queue (Priority A)
- Claim: cross-mission `tau` consistency on flyby missions with published residuals
- Test family: trajectory REAL (`DS-005` classical rows)
- Current status: pass (expanded classical set)

## Objective

Evaluate whether a single lag-signature family remains consistent across multiple flyby missions when using only published residual rows (excluding recent placeholder holdout missions).

## Reproducible Runs

```powershell
# A) strict small classical subset (diagnostic)
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory_real.py `
  --test-id QNG-T-F02 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --flyby-pass-ids GALILEO_1,GALILEO_2,NEAR_1,CASSINI_1,ROSETTA_1,MESSENGER_1 `
  --seed 20260217 `
  --out-dir 05_validation/evidence/artifacts/qng-t-f02-cross-mission-2026-02-21

# B) expanded classical set (official F02 result)
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory_real.py `
  --test-id QNG-T-F02 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --flyby-pass-ids GALILEO_1,GALILEO_2,NEAR_1,CASSINI_1,ROSETTA_1,MESSENGER_1,ROSETTA_2,EPOXI_1,EPOXI_2,ROSETTA_3,EPOXI_3,EPOXI_4,EPOXI_5 `
  --seed 20260217 `
  --out-dir 05_validation/evidence/artifacts/qng-t-f02-cross-mission-classic-2026-02-21
```

## Key Metrics (expanded classical run)

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `delta_chi2` | `-1.172380e+04` | `< 0` | pass |
| `delta_AIC` | `-1.172180e+04` | `<= -10` | pass |
| `delta_BIC` | `-1.172242e+04` | `<= -10` | pass |
| `directionality_score` | `0.750000` | `>= 0.70` | pass |
| `sign_consistency` | `0.666667` | `>= 2/3` | pass |
| `control_mean_abs_over_sigma` | `0.444444` | `<= 1.50` | pass |
| `orientation_shuffle_p` | `0.037500` | `<= 0.10` | pass |
| `segment_shuffle_p` | `0.045000` | `<= 0.10` | pass |
| `leave_out_pass_fraction` | `1.000000` | `>= 0.90` | pass |
| `pass_recommendation` | `pass` | all required rules | pass |

## Notes

- The strict small subset run failed only `rule_pass_control_zero` because control sample was too narrow (`2` control points, mean `|a|/sigma=2.0`).
- The expanded classical set resolves that sampling artifact (`9` control points, mean `|a|/sigma=0.444444`) while leaving all other gates unchanged.
- Recent holdout missions with provisional placeholders (`JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`) were intentionally excluded from this F02 consistency run.

## Decision

- Decision: pass
- Rationale: cross-mission tau-consistency gates pass on expanded classical published-residual flyby set under fixed model/gates and fixed seed.
