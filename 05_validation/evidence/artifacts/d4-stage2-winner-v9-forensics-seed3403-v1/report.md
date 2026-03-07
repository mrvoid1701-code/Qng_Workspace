# D4 Winner V9 Forensics (Seed-Focused)

- generated_utc: `2026-03-07T16:47:04.560289+00:00`
- dataset_id: `DS-006`
- seed: `3403`
- winner_formula_id: `WINNER_V1_M8C`
- train chi2/N (winner, mond, null): `50.985511`, `63.645384`, `307.164193`
- holdout chi2/N (winner, mond, null): `169.100115`, `189.581424`, `289.580653`
- train improve vs null (%): `83.401219`
- holdout improve vs null (%): `41.605175`
- generalization_gap_pp: `41.796044`

## Diagnostic Focus

- inspect `regime_summary.csv` for train vs holdout differences by accel/radial bins
- inspect `holdout_top_worst_galaxies.csv` for concentration of failure pressure
- no thresholds/formulas changed; this run is forensics-only
