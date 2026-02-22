# Negative Controls - QNG-T-027

- Lensing CSV: `data/lensing/cluster_offsets_psz2_strict3.csv`
- Rotation CSV: `data/rotation/rotation_ds006_rotmod.csv`
- Runs per control mode: `12`

## Positive Run (Reference)

- delta_chi2_lens: `-1.127591e+04`
- delta_chi2_rot: `-8.687304e+05`
- delta_chi2_total: `-8.800063e+05`
- delta_aic_total: `-8.800023e+05`
- offset_score: `1.000000`

## Control Gates

- Lensing permutation ratio (median control / positive): `0.001091` (threshold `<= 0.20`) -> `true`
- Rotation permutation ratio (median control / positive): `0.107232` (threshold `<= 0.20`) -> `true`

- Negative-control overall: `true`

Interpretation:
- If control ratios stay low, observed improvements are tied to structure in original pairings.
- If ratios are high, the signal may leak through model flexibility or data construction artifacts.
