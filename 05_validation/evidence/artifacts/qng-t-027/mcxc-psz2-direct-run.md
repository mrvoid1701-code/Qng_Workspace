# QNG-T-027 Direct Run: MCXC x Planck PSZ2

- Date: 2026-02-16
- Dataset: DS-006
- Mode: strict-input (`data_source_mode=provided`)

## Inputs

- Rotation CSV: `data/rotation/rotation_ds006_rotmod.csv` (3391 rows)
- Baryon catalog: `data/lensing/mcxc_catalog_full.csv` (1743 rows)
- SZ-side catalog: `data/lensing/psz2_catalog_full.csv` (1653 rows)
- Built offsets: `data/lensing/cluster_offsets_real.csv` (527 matched pairs, strict-ID filtered)

## Build Summary

- Match mode: `hybrid`
- Strict ID separation gate: `True` (`--strict-id-sep`)
- Matched rows: `527`
- Match split: `id=526`, `sky=1`
- Separation min/median/p90/max (arcmin): `0.101 / 1.263 / 2.830 / 4.835`
- Build report: `05_validation/evidence/artifacts/ds006-cluster-offset-build.md`

## Fit Summary (`fit-summary.csv`)

- `n_lensing=527`
- `n_rotation=3391`
- `delta_chi2=-8.867375e+05`
- `delta_aic=-8.867335e+05`
- `offset_score=1.000000`
- `pass_recommendation=pass`

## Negative Controls (`negative-controls-summary.csv`)

- `negative_control_pass=True`
- `lensing_improvement_ratio_ctrl_vs_pos=5.581038e-04` (gate `<=0.20`)
- `rotation_improvement_ratio_ctrl_vs_pos=0.117021` (gate `<=0.20`)

## Artifacts

- `05_validation/evidence/artifacts/qng-t-027/run-log.txt`
- `05_validation/evidence/artifacts/qng-t-027/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027/lensing-offsets.png`
- `05_validation/evidence/artifacts/qng-t-027/rotation-overlay.png`
- `05_validation/evidence/artifacts/qng-t-027/parameter-stability.md`
- `05_validation/evidence/artifacts/qng-t-027/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027/negative-controls-runs.csv`
- `05_validation/evidence/artifacts/qng-t-027/negative-controls.md`
