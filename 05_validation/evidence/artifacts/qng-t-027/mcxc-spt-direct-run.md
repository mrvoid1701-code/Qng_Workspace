# QNG-T-027 Direct Run: MCXC x SPT (Historical Snapshot)

- Date: 2026-02-16
- Note: superseded by `mcxc-psz2-direct-run.md` for the current enlarged direct set.
- Dataset: DS-006
- Mode: strict-input (`data_source_mode=provided`)

## Inputs

- Rotation CSV: `data/rotation/rotation_ds006_rotmod.csv` (3391 rows)
- Baryon catalog: `data/lensing/mcxc_catalog_full.csv` (1743 rows)
- Lensing/SZ catalog: `data/lensing/spt_sz_table4_catalog.csv` (101 rows)
- Built offsets: `data/lensing/cluster_offsets_real.csv` (10 matched pairs, sky match `<=5 arcmin`)

## Build Summary

- Match mode: `sky`
- Matched rows: `10`
- Separation min/median/max (arcmin): `0.0645 / 0.4119 / 0.8716`
- Build report: `05_validation/evidence/artifacts/ds006-cluster-offset-build.md`

## Fit Summary (`fit-summary.csv`)

- `n_lensing=10`
- `n_rotation=3391`
- `delta_chi2=-8.687555e+05`
- `delta_aic=-8.687515e+05`
- `offset_score=1.000000`
- `pass_recommendation=pass`

## Negative Controls (`negative-controls-summary.csv`)

- `negative_control_pass=True`
- `lensing_improvement_ratio_ctrl_vs_pos=0.031359` (gate `<=0.20`)
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
