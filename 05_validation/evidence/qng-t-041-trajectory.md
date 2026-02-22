# Evidence - QNG-T-041

- Priority: P1
- Claim: QNG-C-086
- Claim statement: `C-086a` directional near-perigee signature is primary; `C-086b v1` is frozen fail history; `C-086b2` is locked calibration pending holdout.
- Derivation: `03_math/derivations/qng-c-086.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-041-trajectory.md`
- Current status: pass

## Objective

Validate the directional component (`C-086a`) under fixed trajectory gates and keep amplitude governance split: `C-086b v1` as falsified history and `C-086b2` as locked calibration with strict out-of-sample holdout.

## Formula Anchor

```text
C-086a: sign(a_res_parallel)=sign(v.gradSigma)
C-086b2: |a_res| = A0*(|v|/v0)^p*(r_p/r0)^(-q)*(|gradSigma|/g0)^s*f_io  (locked calibration + holdout audit)
```

## Dataset / Environment

- Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer)

## Method

- Fit lag term `a_res=-tau(v.nabla)nablaSigma` on trajectory residuals vs GR-only baseline.
- Use DS-005 real pass-level flyby residuals plus Pioneer anchor rows in the same executable run.
- Keep explicit non-gravitational correction fields and enforce fixed controls/robustness gates.
- Run amplitude check in `report-only` mode for `QNG-T-041`; amplitude verdict is tracked separately from `C-086a` under `C-086b v1` and `C-086b2` governance files.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) QNG-T-041 trajectory REAL run (cross-domain, directional gate primary)
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory_real.py `
  --test-id QNG-T-041 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --use-pioneer-anchor `
  --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv `
  --amp-gate-mode report-only `
  --out-dir 05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21 `
  --seed 20260217
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-005 dataset definition | `05_validation/dataset-manifest.json` (verified 2026-02-17; rerun 2026-02-21) | Real trajectory family entry |
| Real flyby data | `data/trajectory/flyby_ds005_real.csv` | Anderson 2008 + Meessen 2017 rows + Horizons-derived holdout geometry rows (`JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`) |
| Pioneer anchor data | `data/trajectory/pioneer_ds005_anchor.csv` | Anderson 2002 Eq.23/Eq.24/Eq.54 anchor rows |
| Prereg amplitude locks | `05_validation/pre-registrations/qng-c-086b-amplitude-band-v1.md`, `05_validation/pre-registrations/qng-c-086b-amplitude-band-v2.md`, `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`, `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md` | v1 frozen fail; b2 calibration+holdout tracked separately; b3 scaling lock is active |
| Holdout registry | `05_validation/pre-registrations/holdout-registry.csv` | Append-only holdout ledger across b2/b3 tracks |
| Runner scripts | `scripts/run_qng_t_028_trajectory_real.py`, `scripts/run_qng_t_041_c086b3_scaling.py` | Real-data trajectory split pipeline + scaling-law pipeline |
| Run config | seed=`20260217`, control_runs=`400`, leave_out_runs=`96`, `amp_gate_mode=report-only` | Post-horizons rerun settings (locked gates/model unchanged) |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/fit-summary.csv` | Main metrics and rule booleans |
| Derived table | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/flyby-derived.csv` | Corrected per-pass acceleration features |
| Mission fits | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/mission-fits.csv` | Per-mission tau and directionality diagnostics |
| Model comparison | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/model-comparison.md` | Same sample/sigma/likelihood checklist |
| Negative controls | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/negative-controls.md` | Orientation/segment/symmetric control diagnostics |
| Robustness report | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/robustness-checks.md` | Leave-out, trim, perigee/whole, inbound/outbound checks |
| Stability report | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/parameter-stability.md` | Mission/bootstrap tau stability |
| Residual plot | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/trajectory-residuals.png` | Observed residual vs baseline vs memory-fit |
| Directionality plot | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/directionality.png` | Feature-residual alignment and fitted slope |
| Run log | `05_validation/evidence/artifacts/qng-t-041-post-horizons-2026-02-21/run-log.txt` | Full command/config snapshot |
| Strict batch summary | `05_validation/evidence/artifacts/qng-t-041-strict-batch-summary.md` | `C-086b v1` strict-mode full + leave-one-out audit |
| b2 calibration summary | `05_validation/evidence/artifacts/qng-t-041-c086b-v2-summary.md` | `C-086b2` calibration lock check (`E1-E3`) |
| b2 holdout summary | `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-summary.md` | `C-086b2` strict out-of-sample holdout (`H1-H3`) |
| b3 scaling fit summary | `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/fit-summary.csv` | `C-086b3` scaling-law status + gates |
| b3 scaling model note | `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/scaling-model.md` | Covariate law, coefficients, uncertainty notes |
| b3 scaling run log | `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/run-log.txt` | Locked holdout IDs and post-ingest holdout verdict details |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-5849.293279` | `< 0` | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-5847.293279` | `<= -10` | pass |
| `delta_BIC = BIC_memory - BIC_baseline` | `-5847.096054` | `<= -10` | pass |
| `delta_chi2_flyby` | `-1.170840e+04` | diagnostic split | pass |
| `delta_chi2_pioneer (corrected)` | `-4430.420979` | diagnostic split | pass |
| `directionality_score` | `0.857143` | `>= 0.70` | pass |
| `sign_consistency` | `0.833333` | `>= 2/3` | pass |
| `orientation_shuffle` | `p=0.022500`, ratio=`0.257381` | `p<=0.10`, ratio `<=0.35` | pass |
| `segment_shuffle` | `p=0.050000`, ratio=`0.845134` | `p<=0.10`, ratio `<=0.95` | pass |
| `control_mean_abs_over_sigma` | `0.400000` | `<=1.50` | pass |
| `leave_out_pass_fraction` | `1.000000` | `>=0.90` | pass |
| `outlier_trim_delta_chi2` | `-4791.390984` | improve vs baseline | pass |
| `amp_median` | `2.271812e-06` | prereg `C-086b v1` band `1e-10..1e-8` | fail (falsified-v1) |
| `amp_median_day_equiv` | `2.083333e-08` | prereg `C-086b v1` support band | fail (falsified-v1) |
| `amp_gate_mode` | `report-only` | split-claim policy | pass |
| Required-rule summary | `all required directional/cross-domain rules true` | pass criteria met | pass |

## C-086b v1 Strict Batch (2026-02-21)

- Batch artifacts:
- `05_validation/evidence/artifacts/qng-t-041-strict-full/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-g1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-g2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-near/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-rosetta/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-batch-summary.md`

- Strict batch outcome: `5/5 fail` on `rule_pass_amp_band` with directional/cross-domain gates still passing.
- Interpretation: `C-086b v1` remains fail under preregistered band; no post-hoc threshold edits were applied.

## C-086b2 Calibration Locked Evaluation (2026-02-21)

- v2 prereg lock:
- `amp_band_min=1e-6`, `amp_band_max=6e-6` (strict gate)
- evaluation sets `E1-E3` locked in prereg file before running.

- v2 artifacts:
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-summary.md`

- b2 calibration outcome:
- strict amp gate: `3/3 pass`
- directional/cross-domain gates: `3/3 pass`
- day-equivalent support band (`1e-8..6e-8`): `0/3 pass` (reported note, not strict gate)

## C-086b2 Holdout Out-of-Sample (2026-02-21)

- Holdout prereg lock:
- `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`

- Holdout artifacts:
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-summary.md`

- Holdout outcome:
- strict holdout gate: `0/3 pass`
- repeated fails include `rule_pass_amp_band=False` and `rule_pass_pioneer_domain=False`
- scope limit: DS-005 currently has only one non-control flyby holdout pass (`CASSINI_1`) outside calibration flyby set

## C-086b3 Scaling-Law Lock (2026-02-21)

- b3 prereg lock:
- `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md`
- append-only registry:
- `05_validation/pre-registrations/holdout-registry.csv`

- b3 artifact bundle:
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/coefficients.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/calibration-predictions.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/holdout-predictions.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b3-scaling/scaling-model.md`

- b3 outcome (post-ingest rerun):
- holdout status: `fail`
- holdout n: `3`
- holdout rmse_log: `15.382645` (gate `<= 1.25`, fail)
- holdout mae_log: `12.883496` (gate `<= 1.00`, fail)
- holdout median_ratio: `1.178824e+08` (gate `[0.50, 2.00]`, fail)
- interpretation: b3 lock is now fully executable on disjoint holdout IDs and no longer blocked. Current run fails holdout gates.
- data-quality note: `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1` rows were ingested with Horizons geometry but provisional residual placeholders (`delta_v_obs=0.0`, `sigma=1.0 mm/s`) pending published OD residual summaries.

## Holdout Status Update (2026-02-21)

- Operational status: ongoing
- Frozen numeric holdout label: blocked_data_pending_official_residuals
- Blocking condition: holdout mission rows still use provisional residual placeholders instead of mission OD/radiometric residual outputs.
- Missions currently blocked for publication-grade numeric holdout:
- `BEPICOLOMBO_1`
- `SOLAR_ORBITER_1`

- Ready-to-run trigger (no model/gate edits):
1. Replace `delta_v_obs_mm_s` and `delta_v_sigma_mm_s` in `data/trajectory/flyby_ds005_real.csv` for holdout missions with official OD/radiometric residual values.
2. Keep all locked prereg files unchanged:
- `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md`
- `05_validation/pre-registrations/holdout-registry.csv`
3. Rerun only the locked holdout command and compare with existing gate thresholds.

## Pass / Fail Criteria

- Pass: Directional/sign and robustness gates pass on same-sample weighted likelihood.
- Fail: Directional gates fail after controls, or consistency collapses under robustness checks.

## Decision

- Decision: pass
- Rationale: `C-086a` directional claim remains pass after post-horizons DS-005 rerun with unchanged gates/model and full control/robustness checks.
- Split note: `C-086b v1` is frozen fail history; `C-086b2` passes calibration lock (`E1-E3`) but fails strict holdout (`H1-H3`); `C-086b3` scaling lock is now executed on disjoint holdout IDs and currently fails under provisional holdout residual placeholders.
- Last updated: 2026-02-21
- Authenticity: silver
- Leakage risk: med
- Negative control: done
