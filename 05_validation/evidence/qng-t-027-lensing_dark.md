# Evidence - QNG-T-027

- Priority: P1
- Claim: QNG-C-058
- Claim statement: Lensing traces gradient Sigma and can be offset from baryonic mass centers.
- Derivation: `03_math/derivations/qng-c-058.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-027-lensing_dark.md`
- Current status: pass

## Objective

Lensing traces gradient Sigma and can be offset from baryonic mass centers.

## Formula Anchor

```text
Phi_lens ~ Sigma
```

## Dataset / Environment

- Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs)

## Method

- Fit Sigma-memory kernel model and compare against GR+particle-DM baseline.
- Keep baseline and memory models on the same sample selection and quality cuts.
- Report both fit quality and parameter stability across subsamples.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Download + parse MCXC full catalog (CDS)
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/534/A109/mcxc.dat" `
  -OutFile "data/lensing/mcxc_full_from_cds.dat"
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/534/A109/ReadMe" `
  -OutFile "data/lensing/mcxc_ReadMe.txt"

.\.venv\Scripts\python.exe scripts\extract_mcxc_cds_catalog.py `
  --input-dat "data/lensing/mcxc_full_from_cds.dat" `
  --out-csv "data/lensing/mcxc_catalog_full.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-mcxc-catalog-extract.md"

# 2) Download + parse Planck PSZ2 catalog (CDS)
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/594/A27/psz2.dat" `
  -OutFile "data/lensing/psz2_full_from_cds.dat"
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/594/A27/ReadMe" `
  -OutFile "data/lensing/psz2_ReadMe.txt"

.\.venv\Scripts\python.exe scripts\extract_psz2_cds_catalog.py `
  --input-dat "data/lensing/psz2_full_from_cds.dat" `
  --out-csv "data/lensing/psz2_catalog_full.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-psz2-catalog-extract.md"

# 3) Build direct baryon-lensing offsets (MCXC x PSZ2)
.\.venv\Scripts\python.exe scripts\build_ds006_cluster_offsets.py `
  --baryon-csv "data/lensing/mcxc_catalog_full.csv" `
  --lensing-csv "data/lensing/psz2_catalog_full.csv" `
  --match-mode hybrid `
  --max-sep-arcmin 5 `
  --strict-id-sep `
  --out-csv "data/lensing/cluster_offsets_real.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-cluster-offset-build.md"

# 4) Strict-input production run
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-027 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --seed 42 `
  --strict-input

# 5) Negative controls
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --n-runs 24 `
  --seed 97
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-006 dataset bundle definition | `05_validation/dataset-manifest.json` (2026-02-16) | Dataset family for lensing + rotation tests |
| Rotation raw download | `C:\Users\tigan\Downloads\Rotmod_LTG\*.dat` | Imported via `scripts/import_ds006_downloads.py` |
| MCXC full catalog (CDS) | `data/lensing/mcxc_full_from_cds.dat` | 1743 X-ray cluster centers |
| Planck PSZ2 catalog (CDS) | `data/lensing/psz2_full_from_cds.dat` | 1653 SZ-side detections |
| Rotation CSV (generated) | `data/rotation/rotation_ds006_rotmod.csv` | 3391 usable rows |
| MCXC baryon CSV (generated) | `data/lensing/mcxc_catalog_full.csv` | 1743 usable rows |
| PSZ2 lensing-side CSV (generated) | `data/lensing/psz2_catalog_full.csv` | 1653 usable rows |
| Offset pairs CSV (generated) | `data/lensing/cluster_offsets_real.csv` | 527 matched pairs (`id=526`, `sky=1`) with strict ID separation gate |
| Baseline model spec | run `RUN-P1-001` | GR + particle-DM reference fit settings |
| Memory model spec | run `RUN-P1-001` | Sigma-memory kernel form + parameter bounds |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Run log | `05_validation/evidence/artifacts/qng-t-027/run-log.txt` | Full command line, software versions, timestamps |
| Fit summary table | `05_validation/evidence/artifacts/qng-t-027/fit-summary.csv` | Baseline vs memory metrics |
| Model comparison | `05_validation/evidence/artifacts/qng-t-027/model-comparison.md` | Same sample/sigma/likelihood/priors checklist |
| Robustness report | `05_validation/evidence/artifacts/qng-t-027/robustness-checks.md` | Leave-10%-out and outlier-trim robustness |
| Robustness CSV | `05_validation/evidence/artifacts/qng-t-027/robustness-checks.csv` | Machine-readable robustness metrics |
| Lensing center-offset plot | `05_validation/evidence/artifacts/qng-t-027/lensing-offsets.png` | Baryonic center vs inferred Sigma center |
| Rotation curve overlay | `05_validation/evidence/artifacts/qng-t-027/rotation-overlay.png` | Baseline and memory fit comparison |
| Parameter stability report | `05_validation/evidence/artifacts/qng-t-027/parameter-stability.md` | Subsample consistency checks |
| Negative-control summary | `05_validation/evidence/artifacts/qng-t-027/negative-controls-summary.csv` | Permutation control gate summary |
| Negative-control run table | `05_validation/evidence/artifacts/qng-t-027/negative-controls-runs.csv` | Per-run control diagnostics |
| Negative-control note | `05_validation/evidence/artifacts/qng-t-027/negative-controls.md` | Human-readable control interpretation |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| Core deltas | `delta_chi2=-8.867375e+05`, `delta_AIC=-8.867335e+05`, `delta_BIC=-8.867209e+05` | `<0`, `<=-10`, `<=-10` | pass |
| Component-normalized deltas | `delta_chi2_lensing/N=-34.169049`, `delta_chi2_rotation/N=-256.187080`, `delta_chi2_total/N=-226.324012` | all negative on same row set | pass |
| Same-sample comparability | See `model-comparison.md` (`same rows`, `same sigma`, `same likelihood`, `same priors policy`) | all checklist rows = pass | pass |
| Parameter stability (`tau`, kernel scale) across subsamples | `cv_tau=0.000000`, `cv_k=0.000000` | Coefficient of variation `< 0.30` | pass |
| Leave-10%-out robustness | `pass_fraction=1.000000`, `delta_chi2 median=-8.016792e+05`, `delta_BIC median=-8.016629e+05` | pass fraction `=1.0`, medians keep sign | pass |
| Top-outlier trim robustness | `trim_fraction=0.05`, `delta_chi2=-8.867203e+05`, `delta_AIC=-8.867163e+05`, `delta_BIC=-8.867038e+05` | all gates pass after trim | pass |
| Lensing center-offset reproduction score | `1.000000` | Meets pre-registered tolerance on validation subset | pass |
| Data coverage | `n_lensing=527`, `n_rotation=3391` | `>=8` / `>=16` usable rows | pass |
| Negative-control gates | `lensing=True (ratio=5.581038e-04)`, `rotation=True (ratio=0.117021)` | control ratios `<= 0.20` | pass |

## Pass / Fail Criteria

- Pass: Offsets/profiles reproduced with stable memory parameters and consistent cross-dataset behavior.
- Fail: Model cannot reproduce offsets/profiles or needs unstable/nonphysical parameter tuning.

## Decision

- Decision: pass
- Rationale: Gold retained under stronger review metrics (delta_chi2/N, BIC, comparability checklist, leave-out and outlier-trim robustness).
- Promotion note: `05_validation/evidence/artifacts/qng-t-027/promotion-gold.md`
- Last updated: 2026-02-17
- Authenticity: gold
- Leakage risk: low
- Negative control: done
