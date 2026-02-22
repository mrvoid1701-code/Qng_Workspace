# Robustness Checks

## Leave-10%-Out

- Runs: `24`
- Fraction removed each run: `0.100000`
- Kept rows per run: lensing=`436`, rotation=`3052`
- delta_chi2 median/min/max: `-7.998745e+05` / `-8.311252e+05` / `-7.064753e+05`
- delta_aic median: `-7.998705e+05`
- delta_bic median: `-7.998582e+05`
- pass fraction (chi2<0, AIC<=-10, BIC<=-10): `1.000000`
- pass all runs: `true`

## Top-Outlier Trim

- Trim fraction: `0.050000`
- Removed rows: lensing=`24`, rotation=`170`
- Kept rows: lensing=`461`, rotation=`3221`
- delta_chi2: `-8.799915e+05`
- delta_aic: `-8.799875e+05`
- delta_bic: `-8.799751e+05`
- trim pass (chi2<0, AIC<=-10, BIC<=-10): `true`
