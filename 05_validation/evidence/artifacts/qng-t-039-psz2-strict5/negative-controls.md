# Negative Controls - QNG-T-027

- Lensing CSV: `data/lensing/cluster_offsets_psz2_strict5.csv`
- Rotation CSV: `data/rotation/rotation_ds006_rotmod.csv`
- Runs per control mode: `24`

## Positive Run (Reference)

- delta_chi2_lens: `-1.800709e+04`
- delta_chi2_rot: `-8.687304e+05`
- delta_chi2_total: `-8.867375e+05`
- delta_aic_total: `-8.867335e+05`
- offset_score: `1.000000`

## Control Gates

- Lensing permutation ratio (median control / positive): `3.934310e-04` (threshold `<= 0.20`) -> `true`
- Rotation permutation ratio (median control / positive): `0.118460` (threshold `<= 0.20`) -> `true`

- Negative-control overall: `true`

Interpretation:
- If control ratios stay low, observed improvements are tied to structure in original pairings.
- If ratios are high, the signal may leak through model flexibility or data construction artifacts.
