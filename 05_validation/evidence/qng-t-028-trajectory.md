# Evidence - QNG-T-028

- Priority: P1
- Claim: QNG-C-060
- Claim statement: Flyby and deep-space anomalies follow directional lag acceleration law.
- Derivation: `03_math/derivations/qng-c-060.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-028-trajectory.md`
- Current status: pass

## Objective

Flyby and deep-space anomalies follow directional lag acceleration law.

## Formula Anchor

```text
a_res ~ -tau*(v.nabla)nablaSigma
```

## Dataset / Environment

- Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer)

## Method

- Fit lag term `a_res=-tau(v.nabla)nablaSigma` on trajectory residuals vs GR-only baseline.
- Use DS-005 real published pass-level Earth-flyby residuals (`flyby_ds005_real.csv`) plus Pioneer anchor rows (`pioneer_ds005_anchor.csv`) in one executable run.
- Keep explicit non-gravitational correction columns in the fit input (`thermal`, `srp`, `maneuver`, `drag`) and require post-correction Pioneer support.
- Define science subset as non-control and non-symmetric passes; evaluate control/symmetric passes as negative controls (C-067-like).
- Enforce robustness on perigee-vs-whole, inbound-vs-outbound, leave-10%-out, and top-outlier trim.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) QNG-T-028 trajectory REAL run (DS-005 published flyby residuals)
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory_real.py `
  --test-id QNG-T-028 `
  --dataset-id DS-005 `
  --flyby-csv data/trajectory/flyby_ds005_real.csv `
  --use-pioneer-anchor `
  --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv `
  --out-dir 05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21 `
  --seed 20260217
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-005 dataset definition | `05_validation/dataset-manifest.json` (verified 2026-02-17; rerun 2026-02-21) | Real trajectory family entry (published pass-level residuals) |
| Real flyby data | `data/trajectory/flyby_ds005_real.csv` | Anderson 2008 + Meessen 2017 compiled pass-level rows |
| Pioneer anchor data | `data/trajectory/pioneer_ds005_anchor.csv` | Anderson 2002 Eq.23/Eq.24/Eq.54 anchor rows |
| Source notes | `data/trajectory/README_ds005_real.md` | Source references and known limits |
| Runner script | `scripts/run_qng_t_028_trajectory_real.py` | Real-data trajectory pipeline with controls + robustness |
| Run config | seed=`20260217`, control_runs=`400`, leave_out_runs=`96`, `use_pioneer_anchor=True` | Post-horizons rerun settings (locked gates unchanged) |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/fit-summary.csv` | Main pass/fail metrics and gate booleans |
| Derived flyby table | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/flyby-derived.csv` | Corrected per-pass derived acceleration features (flyby + Pioneer) |
| Mission fits | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/mission-fits.csv` | Per-mission tau and directionality diagnostics |
| Model comparison | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/model-comparison.md` | Same-sample, same-sigma, same-likelihood checklist |
| Negative controls | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/negative-controls.md` | Orientation/segment/symmetric control diagnostics |
| Robustness report | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/robustness-checks.md` | Leave-out, trim, perigee/whole, inbound/outbound checks |
| Stability report | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/parameter-stability.md` | Mission and bootstrap tau stability |
| Residual plot | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/trajectory-residuals.png` | Observed residual vs baseline vs memory-fit |
| Directionality plot | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/directionality.png` | Feature-residual alignment and fitted slope |
| Run log | `05_validation/evidence/artifacts/qng-t-028-post-horizons-2026-02-21/run-log.txt` | Full command/config snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-5849.293279` | `< 0` | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-5847.293279` | `<= -10` | pass |
| `delta_BIC = BIC_memory - BIC_baseline` | `-5847.096054` | `<= -10` | pass |
| `delta_chi2_flyby` | `-1.170840e+04` | diagnostic split | pass |
| `delta_chi2_pioneer (corrected)` | `-4430.420979` | diagnostic split | pass |
| `tau_fit_total` | `1.368655e-04` | finite and stable | pass |
| `tau_fit_flyby` | `0.002051` | cross-domain sign-consistent | pass |
| `tau_fit_pioneer` | `1.196490e-04` | cross-domain sign-consistent | pass |
| `directionality_score` | `0.857143` | `>= 0.70` | pass |
| `sign_consistency` | `0.833333` | `>= 2/3` | pass |
| `orientation_shuffle` | `p=0.022500`, ratio=`0.257381` | `p<=0.10`, ratio `<=0.35` | pass |
| `segment_shuffle` | `p=0.050000`, ratio=`0.845134` | `p<=0.10`, ratio `<=0.95` | pass |
| `control_mean_abs_over_sigma` | `0.400000` | `<=1.50` | pass |
| `tau_ratio_whole_perigee` | `1.000000` | `[0.85,1.20]` | pass |
| `tau_ratio_inbound_outbound` | `1.066917` (opposite signs) | `<=3.0` | pass |
| `tau_ratio_cross_domain` | `17.140491` | diagnostic (tracked) | pass |
| `leave_out_pass_fraction` | `1.000000` | `>=0.90` | pass |
| `outlier_trim` | `delta_chi2=-4791.390984` | improve vs baseline | pass |
| Required-rule summary | `all required rules true` | pass criteria met | pass |

## Pass / Fail Criteria

- Pass: Single tau-band improves fit metrics and residual direction matches prediction across missions.
- Fail: No significant fit improvement or inconsistent/random tau and sign across missions.

## Decision

- Decision: pass
- Rationale: Post-horizons DS-005 rerun (expanded flyby table, unchanged gates/model) keeps delta-fit, BIC/AIC, directional, negative-control, robustness, and Pioneer post-correction gates as pass.
- Last updated: 2026-02-21
- Authenticity: silver
- Leakage risk: med
- Negative control: done
