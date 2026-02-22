# Evidence - QNG-T-017

- Priority: P2
- Claim: QNG-C-037
- Claim statement: Stability memory field follows convolution Sigma(x,t) = integral K(t-t') chi(x,t') dt'.
- Derivation: `03_math/derivations/qng-c-037.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-017-lensing_dark.md`
- Current status: pass

## Objective

Stability memory field follows convolution Sigma(x,t) = integral K(t-t') chi(x,t') dt'.

## Formula Anchor

```text
Sigma(x,t) = integral_{-inf}^{t} K(t-t')*chi(x,t') dt'
```

## Dataset / Environment

- Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs)

## Method

- Fit Sigma-memory kernel model and compare against GR+particle-DM baseline.
- Keep baseline and memory models on the same sample selection and quality cuts.
- Evaluate both rotation profile fit quality and cross-linked lensing consistency under strict input mode.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Import DS-006-compatible CSV files from local downloads/extracted files
.\.venv\Scripts\python.exe scripts\import_ds006_downloads.py

# 2) Strict-input production run for QNG-T-017 artifacts
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/lensing_ds006_hybrid.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-017" `
  --seed 42 `
  --strict-input
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-006 dataset bundle definition | `05_validation/dataset-manifest.json` (2026-02-16) | Dataset family for lensing + rotation tests |
| Rotation raw download | `C:\Users\tigan\Downloads\Rotmod_LTG\*.dat` | Imported via `scripts/import_ds006_downloads.py` |
| Lensing raw download | `C:\Users\tigan\Downloads\COM_Lensing_4096_R3.00.tgz` | Extracted `MV/PP nlkk.dat` used as proxy source |
| Rotation CSV (generated) | `data/rotation/rotation_ds006_rotmod.csv` | 3391 usable rows |
| Lensing CSV (generated hybrid) | `data/lensing/lensing_ds006_hybrid.csv` | 258 usable rows |
| Baseline model spec | run `RUN-P1-001` | GR + particle-DM reference fit settings |
| Memory model spec | run `RUN-P1-001` | Sigma-memory kernel form + parameter bounds |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Run log | `05_validation/evidence/artifacts/qng-t-017/run-log.txt` | Full command line, software versions, timestamps |
| Fit summary table | `05_validation/evidence/artifacts/qng-t-017/fit-summary.csv` | Baseline vs memory metrics |
| Rotation curve overlay | `05_validation/evidence/artifacts/qng-t-017/rotation-overlay.png` | Baseline and memory fit comparison |
| Lensing center-offset plot | `05_validation/evidence/artifacts/qng-t-017/lensing-offsets.png` | Cross-linked lensing consistency diagnostic |
| Parameter stability report | `05_validation/evidence/artifacts/qng-t-017/parameter-stability.md` | Subsample consistency checks |
| Negative-control summary | `05_validation/evidence/artifacts/qng-t-017/negative-controls-summary.csv` | Permutation control gate summary |
| Negative-control run table | `05_validation/evidence/artifacts/qng-t-017/negative-controls-runs.csv` | Per-run control diagnostics |
| Negative-control note | `05_validation/evidence/artifacts/qng-t-017/negative-controls.md` | Human-readable control interpretation |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `delta_chi2 = chi2_memory - chi2_baseline` | `-8.809870e+05` | `< 0` (memory improves fit) | pass |
| `delta_AIC = AIC_memory - AIC_baseline` | `-8.809830e+05` | `<= -10` (strong support for memory model) | pass |
| Parameter stability (`tau`, kernel scale) across subsamples | `cv_tau=1.124876e-05`, `cv_k=0.000000` | Coefficient of variation `< 0.30` | pass |
| Rotation/lensing data coverage | `n_rotation=3391`, `n_lensing=258` | `>=16` / `>=8` usable rows | pass |
| Gate summary (`rule_pass_delta_chi2`, `rule_pass_delta_aic`, `rule_pass_stability`, `rule_pass_offset_score`) | `True, True, True, True` | all true | pass |
| Negative-control gates | `lensing=True`, `rotation=True` | control ratios `<= 0.20` | pass |

## Pass / Fail Criteria

- Pass: Offsets/profiles reproduced with stable memory parameters and consistent cross-dataset behavior.
- Fail: Model cannot reproduce offsets/profiles or needs unstable/nonphysical parameter tuning.

## Decision

- Decision: pass
- Rationale: Strict-input DS-006 run on Rotmod data + hybrid lensing set (Planck proxy + 2 Clowe-2006 anchors + eROSITA gradients) passes all registered gates. Permutation negative controls pass (lensing/rotation signal collapses under shuffled pairings). Publication-grade gold remains blocked until a larger direct multi-cluster offset catalog replaces proxy-dominated rows.
- Last updated: 2026-02-16
- Authenticity: silver
- Leakage risk: low
- Negative control: done

