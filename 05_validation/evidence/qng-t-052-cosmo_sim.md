# Evidence - QNG-T-052

- Priority: P2
- Claim: QNG-C-107
- Claim statement: Structure formation proceeds by coherent accretion along stability gradients.
- Derivation: `03_math/derivations/qng-c-107.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-052-cosmo_sim.md`
- Current status: pass

## Objective

Structure formation proceeds by coherent accretion along stability gradients.

## Formula Anchor

```text
J = -mu_s * nablaSigma
```

## Dataset / Environment

- Cosmological toy simulation / synthetic catalogs
- Operational dataset used in this run: Planck TT/TE/EE full spectra (R3.01)

## Method

- Build a stability proxy `Sigma(ell)` from smoothed TT/TE/EE spectra.
- Compute `J(ell) = -dSigma/dell` and evaluate local flux convergence at detected extrema.
- Compare baseline (heavy smoothing) vs coherence model (lighter smoothing) using weighted `chi2`.
- Check cross-spectrum coherence via correlation between TT and absolute TE/EE envelopes.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Run Planck CMB coherence pipeline
.\.venv\Scripts\python.exe scripts\run_qng_t_052_cmb_coherence.py `
  --dataset-id DS-002 `
  --tt-file "data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt" `
  --te-file "data/cmb/planck/COM_PowerSpect_CMB-TE-full_R3.01.txt" `
  --ee-file "data/cmb/planck/COM_PowerSpect_CMB-EE-full_R3.01.txt" `
  --out-dir "05_validation/evidence/artifacts/qng-t-052" `
  --ell-min 30 `
  --ell-max 2500 `
  --baseline-window 121 `
  --memory-window 21 `
  --peak-min-distance 60 `
  --prominence-frac 0.02

# 2) Review artifacts and update Workbench row
# - fit-summary.csv
# - parameter-stability.md
# - peak-table.csv
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-002 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Dataset family for QNG-T-050..053 |
| Planck TT full spectrum | `data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt` | Main temperature anisotropy series |
| Planck TE full spectrum | `data/cmb/planck/COM_PowerSpect_CMB-TE-full_R3.01.txt` | Temperature-polarization cross-spectrum |
| Planck EE full spectrum | `data/cmb/planck/COM_PowerSpect_CMB-EE-full_R3.01.txt` | E-mode polarization spectrum |
| QNG v3 reference best-fit summary | `data/cmb/planck/qng_v3_unified_best_fit.txt` | External reference (chi2 summary + parameters) |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Run log | `05_validation/evidence/artifacts/qng-t-052/run-log.txt` | Runtime metadata + dataset reference snapshot |
| Fit summary | `05_validation/evidence/artifacts/qng-t-052/fit-summary.csv` | Core metrics + pass-rule booleans |
| Extrema table | `05_validation/evidence/artifacts/qng-t-052/peak-table.csv` | Detected extrema used in diagnostics |
| Spectrum plots | `05_validation/evidence/artifacts/qng-t-052/tt-spectrum.png`, `te-spectrum.png`, `ee-spectrum.png` | Observed vs baseline vs coherence model |
| Robustness report | `05_validation/evidence/artifacts/qng-t-052/parameter-stability.md` | CV across preprocessing grid |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2_total = chi2_coherence - chi2_baseline` | `-3425.969969` | `< 0` | diagnostic-pass |
| Mean flux-coherence score (TT/TE/EE) | `0.850000` | `>= 0.55` | diagnostic-pass |
| Cross-spectrum corr `TT` vs `|TE|` | `0.377526` | `|corr| >= 0.20` | diagnostic-pass |
| Cross-spectrum corr `TT` vs `|EE|` | `-0.441612` | `|corr| >= 0.20` | diagnostic-pass |
| Gate summary (`rule_delta_chi2`, `rule_coherence`, `rule_cross_spectrum_corr`) | `True, True, True` | All `True` | diagnostic-pass |
| Auto recommendation | `pass` | diagnostic only | informational |

## Pass / Fail Criteria

- Pass: Predicted scaling/signatures appear across reasonable parameter bands without ad-hoc tuning.
- Fail: Signatures absent or only appear under nonphysical/extreme parameter tuning.

## Decision

- Decision: pass
- Rationale: Planck TT/TE/EE diagnostics satisfy all registered criteria in the current DS-002 scope.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
