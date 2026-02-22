# Pre-Registration: QNG-C-086b3 Scaling Law v1

- Claim fragment: `C-086b3` (covariate-dependent amplitude model)
- Parent claim: `QNG-C-086`
- Created: `2026-02-21`
- Status: locked; holdout executed (see run record, 2026-02-21)
- Governance: `C-086b v1` remains permanent fail history; `C-086b2` remains calibration/holdout fail; `C-086b3` must pass a new disjoint holdout.

## Locked Model Form

```text
log(A_obs + eps) =
  b0
  + b1 * log(v_p / v0)
  + b2 * log((h_p + h0) / h0)
  + b3 * log(|grad_g| / g0)
  + b4 * log(1 + geom_io)
  + b5 * log(1 + non_grav / ng0)
  + e
```

Where:
- `A_obs`: perigee-window residual amplitude (`|a_obs_perigee|`)
- `h_p`: perigee altitude
- `v_p`: perigee speed
- `|grad_g|`: GR-baseline proxy for `|nabla g|`
- `geom_io`: inbound/outbound geometry proxy (`|cos(delta_in)-cos(delta_out)|`)
- `non_grav`: control proxy from explicit thermal/SRP/maneuver/drag columns

## Locked Data + Policy

- Dataset: `DS-005` (`data/trajectory/flyby_ds005_real.csv`)
- Runner: `scripts/run_qng_t_041_c086b3_scaling.py`
- No post-hoc edits to:
- covariate set
- target transform
- holdout IDs
- acceptance gates

## Locked Holdout (Disjoint From C-086b2 Holdout IDs)

- `B3-H1`: flyby=`JUNO_1`; pioneer=`P10_EQ23,P11_EQ24`
- `B3-H2`: flyby=`BEPICOLOMBO_1`; pioneer=`P10_EQ23,P10P11_FINAL`
- `B3-H3`: flyby=`SOLAR_ORBITER_1`; pioneer=`P11_EQ24,P10P11_FINAL`

Registry rule:
- all holdout rows must be appended in `05_validation/pre-registrations/holdout-registry.csv`
- holdout registry is append-only (no in-place edits)

## Locked Acceptance Gates (Out-of-Sample)

- `n_holdout >= 3`
- `holdout_rmse_log <= 1.25`
- `holdout_mae_log <= 1.00`
- `0.50 <= holdout_median_ratio <= 2.00`

Pass condition:
- all holdout gates pass with unchanged locked configuration.

Fail/Blocked condition:
- any holdout gate fails -> `fail`
- missing holdout rows -> `blocked` (data-ingest blocker, not pass)

## Repro Command (Locked)

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_041_c086b3_scaling.py `
  --test-id QNG-T-041 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --holdout-pass-ids JUNO_1,BEPICOLOMBO_1,SOLAR_ORBITER_1 `
  --out-dir 05_validation/evidence/artifacts/qng-t-041-c086b3-scaling
```

## Execution Record

- `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1-run-record-2026-02-21.md`
