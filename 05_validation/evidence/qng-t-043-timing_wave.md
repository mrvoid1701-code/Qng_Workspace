# Evidence - QNG-T-043

- Priority: P1
- Claim: QNG-C-091
- Claim statement: If gravitational-wave propagation depends on tau(chi), ringdown distortions scale with mass asymmetry and delay.
- Derivation: `03_math/derivations/qng-c-091.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-043-timing_wave.md`
- Current status: pass

## Objective

If gravitational-wave propagation depends on tau(chi), ringdown distortions scale with mass asymmetry and delay.

## Formula Anchor

```text
Delta h ~ A_asym * tau(chi) * f_ringdown(t)
```

## Dataset / Environment

- Timing/waveforms (GPS residuals, binary pulsars, LIGO/Virgo/KAGRA)

## Method

- Search tau/chi-linked corrections in TOA/clock/ringdown residual channels after baseline centering.
- Run synthetic DS-008 diagnostic suite across six timing/wave channels.
- Fit tau-grid memory template and chi scaling per channel; compare against zero-memory baseline.
- Enforce correlation/SNR/stability/sign gates before pass recommendation.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) QNG-T-043 timing/wave diagnostic run (DS-008 synthetic)
.\.venv\Scripts\python.exe scripts\run_qng_t_042_timing_wave.py --dataset-id DS-008 --seed 9153 --tau-truth 38 --chi-truth 3.9e-07 --noise-sigma 1.9e-07 --out-dir "05_validation/evidence/artifacts/qng-t-043"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-008 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Synthetic diagnostic mode for timing/wave family |
| Runner script | `scripts/run_qng_t_042_timing_wave.py` | Stdlib-only timing/wave pipeline |
| Channel set | `GPS-A, GPS-B, PSR-B1534, PSR-J0737, GW150914, GW170817` | Multi-channel robustness check |
| Run config | seed=`9153`, samples=`1200`, dt=`1.0`, tau_truth=`38`, chi_truth=`3.9e-07`, noise_sigma=`1.9e-07` | Fixed reproducible settings |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-043/fit-summary.csv` | Main pass/fail metrics and gate booleans |
| Time-series sample | `05_validation/evidence/artifacts/qng-t-043/timeseries-sample.csv` | Driver/residual samples per channel |
| Channel fits | `05_validation/evidence/artifacts/qng-t-043/channel-fits.csv` | Per-channel tau/chi fit diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-043/parameter-stability.md` | CV statistics for tau and chi |
| Residual plot | `05_validation/evidence/artifacts/qng-t-043/residual-timeseries.png` | Residual vs baseline vs memory-fit (representative channel) |
| Echo template plot | `05_validation/evidence/artifacts/qng-t-043/echo-template.png` | Driver vs memory-template overlay |
| Run log | `05_validation/evidence/artifacts/qng-t-043/run-log.txt` | Full command/config snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-3.872664e+06` | `< 0` | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-3.872660e+06` | `<= -10` | pass |
| `tau_fit_mean` | `36.000000` | finite and stable | pass |
| `chi_fit_mean` | `3.882182e-07` | finite and stable | pass |
| `corr_mean` | `0.998804` | `>= 0.55` | pass |
| `snr_mean` | `20.569405` | `>= 1.50` | pass |
| `cv_tau`, `cv_chi` | `0.000000`, `0.068751` | both `< 0.35` | pass |
| `sign_consistency` | `1.000000` | `>= 0.80` | pass |
| Gate summary | `True, True, True, True, True, True` | all true | pass |

## Pass / Fail Criteria

- Pass: Residual pattern remains significant and parameter-consistent after robustness checks.
- Fail: No robust tau/chi-linked residual remains once systematics and noise models are applied.

## Decision

- Decision: pass
- Rationale: Synthetic DS-008 timing/wave run passed all gates; keep synthetic caveat until real timing/wave validation.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
