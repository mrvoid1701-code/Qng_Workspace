# Robustness Checks

## Leave-10%-Out

- Runs: `24`
- Fraction removed each run: `0.100000`
- Kept rows per run: lensing=`474`, rotation=`3052`
- delta_chi2 median/min/max: `-8.121151e+05` / `-8.456896e+05` / `-7.435397e+05`
- delta_aic median: `-8.121111e+05`
- delta_bic median: `-8.120988e+05`
- pass fraction (chi2<0, AIC<=-10, BIC<=-10): `1.000000`
- pass all runs: `true`

## Top-Outlier Trim

- Trim fraction: `0.050000`
- Removed rows: lensing=`26`, rotation=`170`
- Kept rows: lensing=`501`, rotation=`3221`
- delta_chi2: `-8.867203e+05`
- delta_aic: `-8.867163e+05`
- delta_bic: `-8.867038e+05`
- trim pass (chi2<0, AIC<=-10, BIC<=-10): `true`
