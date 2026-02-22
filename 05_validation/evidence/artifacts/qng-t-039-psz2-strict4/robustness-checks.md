# Robustness Checks

## Leave-10%-Out

- Runs: `24`
- Fraction removed each run: `0.100000`
- Kept rows per run: lensing=`461`, rotation=`3052`
- delta_chi2 median/min/max: `-7.972577e+05` / `-8.302616e+05` / `-7.292905e+05`
- delta_aic median: `-7.972537e+05`
- delta_bic median: `-7.972413e+05`
- pass fraction (chi2<0, AIC<=-10, BIC<=-10): `1.000000`
- pass all runs: `true`

## Top-Outlier Trim

- Trim fraction: `0.050000`
- Removed rows: lensing=`26`, rotation=`170`
- Kept rows: lensing=`486`, rotation=`3221`
- delta_chi2: `-8.835939e+05`
- delta_aic: `-8.835899e+05`
- delta_bic: `-8.835774e+05`
- trim pass (chi2<0, AIC<=-10, BIC<=-10): `true`
