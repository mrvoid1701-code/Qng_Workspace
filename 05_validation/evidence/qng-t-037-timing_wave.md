# Evidence - QNG-T-037

- Priority: P2
- Claim: QNG-C-078
- Claim statement: Effective causal cone is modified to r less-or-equal c times (t - tau(chi)).
- Derivation: `03_math/derivations/qng-c-078.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-037-timing_wave.md`
- Current status: pass

## Objective

Effective causal cone is modified to r less-or-equal c times (t - tau(chi)).

## Formula Anchor

```text
r <= c*(t - tau(chi))
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

# 1) QNG-T-037 timing/wave diagnostic run (DS-008 synthetic)
.\.venv\Scripts\python.exe scripts\run_qng_t_042_timing_wave.py --dataset-id DS-008 --seed 9486 --tau-truth 32 --chi-truth 3.4e-07 --noise-sigma 1.7e-07 --out-dir "05_validation/evidence/artifacts/qng-t-037"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-008 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Synthetic diagnostic mode for timing/wave family |
| Runner script | `scripts/run_qng_t_042_timing_wave.py` | Stdlib-only timing/wave pipeline |
| Channel set | `GPS-A, GPS-B, PSR-B1534, PSR-J0737, GW150914, GW170817` | Multi-channel robustness check |
| Run config | seed=`9486`, samples=`1200`, dt=`1.0`, tau_truth=`32`, chi_truth=`3.4e-07`, noise_sigma=`1.7e-07` | Fixed reproducible settings |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-037/fit-summary.csv` | Main pass/fail metrics and gate booleans |
| Time-series sample | `05_validation/evidence/artifacts/qng-t-037/timeseries-sample.csv` | Driver/residual samples per channel |
| Channel fits | `05_validation/evidence/artifacts/qng-t-037/channel-fits.csv` | Per-channel tau/chi fit diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-037/parameter-stability.md` | CV statistics for tau and chi |
| Residual plot | `05_validation/evidence/artifacts/qng-t-037/residual-timeseries.png` | Residual vs baseline vs memory-fit (representative channel) |
| Echo template plot | `05_validation/evidence/artifacts/qng-t-037/echo-template.png` | Driver vs memory-template overlay |
| Run log | `05_validation/evidence/artifacts/qng-t-037/run-log.txt` | Full command/config snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-3.511281e+06` | `< 0` | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-3.511277e+06` | `<= -10` | pass |
| `tau_fit_mean` | `30.000000` | finite and stable | pass |
| `chi_fit_mean` | `3.361792e-07` | finite and stable | pass |
| `corr_mean` | `0.998558` | `>= 0.55` | pass |
| `snr_mean` | `18.679405` | `>= 1.50` | pass |
| `cv_tau`, `cv_chi` | `0.000000`, `0.073534` | both `< 0.35` | pass |
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
