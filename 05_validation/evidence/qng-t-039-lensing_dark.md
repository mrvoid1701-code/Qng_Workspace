# Evidence - QNG-T-039

- Priority: P1
- Claim: QNG-C-082
- Claim statement: Rotation-curve excess can be explained by historical Sigma lag from prior mass distributions.
- Derivation: `03_math/derivations/qng-c-082.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-039-lensing_dark.md`
- Current status: pass

## Objective

Rotation-curve excess can be explained by historical Sigma lag from prior mass distributions.

## Formula Anchor

```text
v_c(r)^2/r = g_baryon(r) + g_memory(r)
```

## Dataset / Environment

- Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs)

## Method

- Fit Sigma-memory kernel model and compare against GR+particle-DM baseline.
- Keep baseline and memory models on the same sample selection and quality cuts.
- Use strict direct-catalog lensing offsets (MCXC x PSZ2) as the primary production path.
- Require robustness under separation-threshold sweeps and an independent direct-catalog anchor.
- Require permutation negative controls for each promoted run slice.
- Run a rotation-only baseline-upgrade check with comparable model flexibility (1 fitted parameter vs 1 fitted parameter) on the same rotation sample and likelihood.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Primary direct-catalog production run (MCXC x PSZ2 offsets)
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-039 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-direct" `
  --seed 142 `
  --strict-input

# 2) Primary negative controls (extended)
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-direct" `
  --n-runs 48 `
  --seed 197

# 3) Separation-threshold robustness sweeps (PSZ2 strict3/4/5)
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-039 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict3.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict3" `
  --seed 143 `
  --strict-input
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-039 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict4.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict4" `
  --seed 144 `
  --strict-input
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-039 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict5.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict5" `
  --seed 145 `
  --strict-input

# 4) Negative controls for robustness sweeps
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict3.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict3" `
  --n-runs 24 `
  --seed 198
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict4.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict4" `
  --n-runs 24 `
  --seed 200
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_psz2_strict5.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-psz2-strict5" `
  --n-runs 24 `
  --seed 201

# 5) Independent direct-catalog anchor (MCXC x SPT) + controls
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --test-id QNG-T-039 `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_spt_anchor.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-spt-anchor" `
  --seed 146 `
  --strict-input
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_spt_anchor.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-spt-anchor" `
  --n-runs 24 `
  --seed 199

# 6) Rotation baseline-upgrade check (publish-defensibility)
.\.venv\Scripts\python.exe scripts\run_qng_t_039_rotation_baseline_upgrade.py `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-039-baseline-upgrade" `
  --seed 20260221
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-006 dataset bundle definition | `05_validation/dataset-manifest.json` (2026-02-16) | Dataset family for lensing + rotation tests |
| Rotation raw download | `C:\Users\tigan\Downloads\Rotmod_LTG\*.dat` | Imported via `scripts/import_ds006_downloads.py` |
| MCXC full catalog (CDS) | `data/lensing/mcxc_full_from_cds.dat` | Baryonic X-ray cluster centers |
| Planck PSZ2 catalog (CDS) | `data/lensing/psz2_full_from_cds.dat` | SZ-side detection catalog |
| SPT SZ catalog (Table 4 extraction) | `data/lensing/spt_sz_table4_catalog.csv` | Independent direct-catalog anchor |
| Rotation CSV (generated) | `data/rotation/rotation_ds006_rotmod.csv` | 3391 usable rows |
| Direct offsets primary CSV | `data/lensing/cluster_offsets_real.csv` | 527 matched pairs with strict ID-separation gate |
| Direct offsets strict3 CSV | `data/lensing/cluster_offsets_psz2_strict3.csv` | 485 matched pairs |
| Direct offsets strict4 CSV | `data/lensing/cluster_offsets_psz2_strict4.csv` | 512 matched pairs |
| Direct offsets strict5 CSV | `data/lensing/cluster_offsets_psz2_strict5.csv` | 527 matched pairs |
| Direct offsets SPT anchor CSV | `data/lensing/cluster_offsets_spt_anchor.csv` | 10 matched pairs |
| Baseline model spec | null + upgraded check (`2026-02-21`) | Null baseline: `v_model=sqrt(baryon_term)` (fixed). Upgraded baseline: `v_model=sqrt(baryon_term + a_flex*halo_proxy)`, prior `a_flex>=0` |
| Memory model spec | production + upgrade audit (`2026-02-21`) | `v_model=sqrt(baryon_term + k_memory*history_term)`, prior `k_memory>=0` |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Primary run log | `05_validation/evidence/artifacts/qng-t-039-direct/run-log.txt` | Full command line, software versions, timestamps |
| Primary fit summary | `05_validation/evidence/artifacts/qng-t-039-direct/fit-summary.csv` | Baseline vs memory metrics |
| Primary model comparison | `05_validation/evidence/artifacts/qng-t-039-direct/model-comparison.md` | Same sample/sigma/likelihood/priors checklist |
| Primary robustness report | `05_validation/evidence/artifacts/qng-t-039-direct/robustness-checks.md` | Leave-10%-out and outlier-trim robustness |
| Primary robustness CSV | `05_validation/evidence/artifacts/qng-t-039-direct/robustness-checks.csv` | Machine-readable robustness metrics |
| Primary rotation overlay | `05_validation/evidence/artifacts/qng-t-039-direct/rotation-overlay.png` | Baseline and memory fit comparison |
| Primary lensing offsets | `05_validation/evidence/artifacts/qng-t-039-direct/lensing-offsets.png` | Cross-linked lensing consistency diagnostic |
| Primary stability report | `05_validation/evidence/artifacts/qng-t-039-direct/parameter-stability.md` | Subsample consistency checks |
| Primary negative-control summary | `05_validation/evidence/artifacts/qng-t-039-direct/negative-controls-summary.csv` | Permutation control gate summary |
| Robustness strict3 summary | `05_validation/evidence/artifacts/qng-t-039-psz2-strict3/fit-summary.csv` | Separation threshold 3 arcmin |
| Robustness strict4 summary | `05_validation/evidence/artifacts/qng-t-039-psz2-strict4/fit-summary.csv` | Separation threshold 4 arcmin |
| Robustness strict5 summary | `05_validation/evidence/artifacts/qng-t-039-psz2-strict5/fit-summary.csv` | Separation threshold 5 arcmin |
| SPT anchor summary | `05_validation/evidence/artifacts/qng-t-039-spt-anchor/fit-summary.csv` | Independent direct-catalog anchor |
| Promotion note | `05_validation/evidence/artifacts/qng-t-039-direct/promotion-gold.md` | Gold promotion basis and artifact index |
| Baseline-upgrade summary | `05_validation/evidence/artifacts/qng-t-039-baseline-upgrade/fit-summary.csv` | Rotation-only equal-flexibility check |
| Baseline-upgrade comparison | `05_validation/evidence/artifacts/qng-t-039-baseline-upgrade/model-comparison.md` | Same sample/sigma/likelihood + priors table |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| Primary direct run (`cluster_offsets_real`) | `delta_chi2=-8.867375e+05`, `delta_AIC=-8.867335e+05`, `delta_BIC=-8.867209e+05`, `n_lensing=527`, `n_rotation=3391` | `delta_chi2<0`, `delta_AIC<=-10`, `delta_BIC<=-10` | pass |
| Component-normalized deltas | `delta_chi2_lensing/N=-34.169049`, `delta_chi2_rotation/N=-256.187080`, `delta_chi2_total/N=-226.324012` | all negative on same row set | pass |
| Same-sample comparability | See `model-comparison.md` (`same rows`, `same sigma`, `same likelihood`, `same priors policy`) | all checklist rows = pass | pass |
| Primary parameter stability | `cv_tau=0.000000`, `cv_k=0.000000` | Coefficient of variation `< 0.30` | pass |
| Primary negative controls | `lensing_ratio=5.875315e-04`, `rotation_ratio=0.122840` | control ratios `<= 0.20` | pass |
| Leave-10%-out robustness | `pass_fraction=1.000000`, `delta_chi2 median=-8.030311e+05`, `delta_BIC median=-8.030147e+05` | pass fraction `=1.0`, medians keep sign | pass |
| Top-outlier trim robustness | `trim_fraction=0.05`, `delta_chi2=-8.867203e+05`, `delta_AIC=-8.867163e+05`, `delta_BIC=-8.867038e+05` | all gates pass after trim | pass |
| Robustness sweep strict3/4/5 | `delta_chi2=-8.800063e+05 / -8.836111e+05 / -8.867375e+05` | all `< 0` | pass |
| Robustness negative controls strict3/4/5 | lensing ratios `0.001031 / 3.161012e-04 / 3.934310e-04`; rotation ratios `0.121095 / 0.108747 / 0.118460` | all `<= 0.20` | pass |
| Independent anchor (MCXC x SPT) | `delta_chi2=-8.687555e+05`, `delta_AIC=-8.687515e+05`, `n_lensing=10` | pass with independent direct-catalog source | pass |
| SPT-anchor negative controls | `lensing_ratio=0.039395`, `rotation_ratio=0.118496` | control ratios `<= 0.20` | pass |
| Rotation baseline-upgrade (1p vs 1p) | `delta_chi2_memory_vs_flex=-4.439109e+05`, `delta_AIC=-4.439109e+05`, `delta_BIC=-4.439109e+05`, `dchi2/N=-130.908564` | memory must beat equal-flexibility baseline | pass |

## Pass / Fail Criteria

- Pass: Offsets/profiles reproduced with stable memory parameters and consistent cross-dataset behavior.
- Fail: Model cannot reproduce offsets/profiles or needs unstable/nonphysical parameter tuning.

## Decision

- Decision: pass
- Rationale: Gold promotion remains supported after adding reviewer-grade checks (delta_chi2/N, BIC, same-likelihood table, leave-out and outlier-trim) plus a rotation equal-flexibility baseline-upgrade check; rerun after metric-v3 stabilization reproduces the same direct/robustness/control outcomes.
- Promotion note: `05_validation/evidence/artifacts/qng-t-039-direct/promotion-gold.md`
- Last updated: 2026-02-21
- Authenticity: gold
- Leakage risk: low
- Negative control: done
