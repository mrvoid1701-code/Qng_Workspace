# Negative Controls - QNG-T-027

- Lensing CSV: `data/lensing/cluster_offsets_spt_anchor.csv`
- Rotation CSV: `data/rotation/rotation_ds006_rotmod.csv`
- Runs per control mode: `12`

## Positive Run (Reference)

- delta_chi2_lens: `-25.132905`
- delta_chi2_rot: `-8.687304e+05`
- delta_chi2_total: `-8.687555e+05`
- delta_aic_total: `-8.687515e+05`
- offset_score: `1.000000`

## Control Gates

- Lensing permutation ratio (median control / positive): `0.077182` (threshold `<= 0.20`) -> `true`
- Rotation permutation ratio (median control / positive): `0.107232` (threshold `<= 0.20`) -> `true`

- Negative-control overall: `true`

Interpretation:
- If control ratios stay low, observed improvements are tied to structure in original pairings.
- If ratios are high, the signal may leak through model flexibility or data construction artifacts.
