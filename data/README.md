# Data Inputs (Validation)

This folder contains local input files for empirical validation runs.

## QNG-T-027 expected CSV inputs

- `data/lensing/lensing_sample.csv`
- `data/rotation/rotation_sample.csv`

Important:
- Current files are schema examples only, not production datasets.
- For a valid DS-006 run, replace them with real data.
- The runner requires at least:
  - 8 usable lensing rows
  - 16 usable rotation rows

Accepted lensing columns:
- required: `sigma_grad_x`, `sigma_grad_y`
- plus either:
  - `obs_dx`, `obs_dy`
  - or `baryon_x`, `baryon_y`, `lens_x`, `lens_y`
- optional: `system_id`, `sigma`

Accepted rotation columns:
- required: `radius`, `v_obs`
- optional: `system_id`, `v_err`, `baryon_term`, `history_term`

## QNG-T-052 expected Planck inputs

- `data/cmb/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt`
- `data/cmb/planck/COM_PowerSpect_CMB-TE-full_R3.01.txt`
- `data/cmb/planck/COM_PowerSpect_CMB-EE-full_R3.01.txt`
- optional reference: `data/cmb/planck/qng_v3_unified_best_fit.txt`

Expected format for TT/TE/EE text files:
- comment header line starting with `#`
- numeric columns:
  - `ell`
  - `Dl`
  - `-dDl`
  - `+dDl`

Current QNG-T-052 pipeline:
- script: `scripts/run_qng_t_052_cmb_coherence.py`
- output artifacts: `05_validation/evidence/artifacts/qng-t-052/`

## DS-006 local imports (QNG-T-027 / QNG-T-039)

Generated from local downloads via:
- `.\.venv\Scripts\python.exe scripts\import_ds006_downloads.py`

Outputs:
- `data/rotation/rotation_ds006_rotmod.csv` (from `Downloads/Rotmod_LTG/*.dat`)
- `data/lensing/lensing_ds006_planck_proxy.csv` (from Planck `MV/PP nlkk.dat` proxy mapping)
- `data/lensing/lensing_ds006_hybrid.csv` (proxy rows + direct Clowe anchors + eROSITA gradient features)
- extracted Planck lensing tables:
  - `data/lensing/planck_lensing_4096_r3/COM_Lensing_4096_R3.00/MV/nlkk.dat`
  - `data/lensing/planck_lensing_4096_r3/COM_Lensing_4096_R3.00/PP/nlkk.dat`

Important:
- Rotation file is direct parsed observational rotation-curve data.
- Lensing file is a reproducible proxy derived from Planck lensing power tables, used for workflow execution.
- Hybrid file is built with `scripts/build_ds006_hybrid_lensing.py` and is the current DS-006 run input.
- For publication-grade DS-006 evidence, replace proxy-dominated rows with larger direct cluster lensing offset catalogs.
