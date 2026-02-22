# Evidence - QNG-T-010

- Priority: P2
- Claim: QNG-C-025
- Claim statement: Stratonic lag produces residual gravitational forces in dynamic systems.
- Derivation: `03_math/derivations/qng-c-025.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-010-trajectory.md`
- Current status: pass

## Objective

Stratonic lag produces residual gravitational forces in dynamic systems.

## Formula Anchor

```text
a_res ~ -tau * (v . nabla) nablaSigma
```

## Dataset / Environment

- Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer)

## Method

- Fit lag term `a_res=-tau(v.nabla)nablaSigma` on trajectory residuals vs GR-only baseline.
- Run synthetic DS-005 diagnostic telemetry across six missions with centered residual fitting.
- Estimate global `tau_fit` and check directional agreement/sign consistency across missions.
- Enforce stability and amplitude-band gates before pass recommendation.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) QNG-T-010 trajectory diagnostic run (DS-005 synthetic)
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory.py --dataset-id DS-005 --seed 852 --tau-truth 2.8e-09 --noise-sigma 5.4e-10 --out-dir "05_validation/evidence/artifacts/qng-t-010"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-005 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Synthetic diagnostic mode for trajectory family |
| Runner script | `scripts/run_qng_t_028_trajectory.py` | Stdlib-only trajectory pipeline |
| Mission set | `Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer` | Six-mission directional consistency check |
| Run config | seed=`852`, points/mission=`120`, tau_truth=`2.8e-09`, noise_sigma=`5.4e-10` | Fixed reproducible settings |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-010/fit-summary.csv` | Main pass/fail metrics and gate booleans |
| Telemetry sample | `05_validation/evidence/artifacts/qng-t-010/telemetry-sample.csv` | Centered feature/residual series |
| Mission fits | `05_validation/evidence/artifacts/qng-t-010/mission-fits.csv` | Per-mission tau and directionality diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-010/parameter-stability.md` | CV statistics for tau estimates |
| Residual plot | `05_validation/evidence/artifacts/qng-t-010/trajectory-residuals.png` | Observed residual vs baseline vs memory-fit |
| Directionality plot | `05_validation/evidence/artifacts/qng-t-010/directionality.png` | Feature-residual alignment and fitted slope |
| Run log | `05_validation/evidence/artifacts/qng-t-010/run-log.txt` | Full command/config snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-1.260508e+04` | `< 0` | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-1.260308e+04` | `<= -10` | pass |
| `tau_fit` | `2.777934e-09` | finite and stable | pass |
| `directionality_score` | `0.965278` | `>= 0.62` | pass |
| `sign_consistency` | `1.000000` | `>= 0.80` | pass |
| `amp_median` | `1.884793e-09` | `1e-10 <= amp <= 1e-8` | pass |
| `cv_tau` | `0.012407` | `< 0.35` | pass |
| Gate summary | `True, True, True, True, True, True` | all true | pass |

## Pass / Fail Criteria

- Pass: Single tau-band improves fit metrics and residual direction matches prediction across missions.
- Fail: No significant fit improvement or inconsistent/random tau and sign across missions.

## Decision

- Decision: pass
- Rationale: Synthetic DS-005 trajectory run passed all gates; keep synthetic caveat until real telemetry validation.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
