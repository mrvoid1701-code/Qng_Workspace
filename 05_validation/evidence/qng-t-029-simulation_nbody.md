# Evidence - QNG-T-029

- Priority: P1
- Claim: QNG-C-062
- Claim statement: N-body simulations with memory kernels should reproduce QNG-consistent structure signatures.
- Derivation: `03_math/derivations/qng-c-062.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-029-simulation_nbody.md`
- Current status: pass

## Objective

N-body simulations with memory kernels should reproduce QNG-consistent structure signatures.

## Formula Anchor

```text
Sigma^n = sum_{m<=n} w_{n-m}*chi^m, w_r~exp(-r*dt/tau)
```

## Dataset / Environment

- Discrete/N-body simulation environment

## Method

- Run memory-kernel N-body and compare morphology/kinematics against instantaneous-gravity baseline.
- Use a fixed-seed synthetic DS-003 simulation suite with identical initial conditions across models.
- Fit baseline (`g_base`) and memory (`tau`, `k_memory`) by minimizing profile+offset+coherence error.
- Evaluate robustness across multiple seeds and require stability (`CV`) in recovered memory parameters.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) QNG-T-029 strict simulation run (DS-003)
.\.venv\Scripts\python.exe scripts\run_qng_t_029_simulation_nbody.py `
  --dataset-id DS-003 `
  --runs 12 `
  --steps 160 `
  --particles 140 `
  --seed 730 `
  --dt 0.06 `
  --noise-scale 1.0 `
  --truth-tau 1.30 `
  --truth-k 0.85 `
  --out-dir "05_validation/evidence/artifacts/qng-t-029"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-003 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Discrete/N-body simulation family |
| Runner script | `scripts/run_qng_t_029_simulation_nbody.py` | Stdlib-only executable pipeline for QNG-T-029 |
| Parameter grid | `tau={0.45..2.20}`, `k={0.25..1.05}`, `g_base={0.82..1.18}` | Fixed candidate sets for reproducible fitting |
| Simulation config | runs=`12`, steps=`160`, particles=`140`, seed base=`730` | Robustness and stability evaluation |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-029/fit-summary.csv` | Main pass/fail metrics and gate booleans |
| Robustness per run | `05_validation/evidence/artifacts/qng-t-029/robustness-runs.csv` | Seed-by-seed fit diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-029/parameter-stability.md` | CV statistics for fitted parameters |
| Profile overlay plot | `05_validation/evidence/artifacts/qng-t-029/profile-overlay.png` | Observed vs baseline vs memory radial profile |
| Centroid offset plot | `05_validation/evidence/artifacts/qng-t-029/centroid-offset.png` | Offset time-series comparison |
| Simulation time-series | `05_validation/evidence/artifacts/qng-t-029/simulation-timeseries.csv` | Stepwise offset series |
| Run log | `05_validation/evidence/artifacts/qng-t-029/run-log.txt` | Full command/config snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory_total - chi2_baseline_total` | `-671.489291` | `< 0` (memory improves fit) | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-669.489291` | `<= -10` (strong support) | pass |
| Profile RMSE mean (`baseline -> memory`) | `0.016510 -> 0.006362` (`gain=0.614669`) | memory `<= 0.90 * baseline` | pass |
| Centroid-offset error mean (`baseline -> memory`) | `0.036633 -> 0.011812` (`gain=0.677570`) | memory `<= 0.90 * baseline` | pass |
| Coherence error mean (`baseline -> memory`) | `0.087612 -> 0.011264` (`gain=0.871430`) | informational | pass |
| Stability (`cv_tau`, `cv_k_memory`) | `0.157334`, `0.091268` | both `< 0.30` | pass |
| Gate summary (`delta_chi2`, `delta_aic`, `profile`, `offset`, `stability`) | `True, True, True, True, True` | all true | pass |

## Pass / Fail Criteria

- Pass: Kernel model improves target metrics (offsets, halo evolution, structure coherence) reproducibly.
- Fail: No metric improvement or unstable dynamics under realistic parameter ranges.

## Decision

- Decision: pass
- Rationale: DS-003 synthetic N-body suite passes delta-fit, profile/offset, and stability gates for QNG-T-029.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
