# Robustness Checks

## Leave-10%-Out

- Runs: `24`
- Fraction removed each run: `0.100000`
- Kept rows per run: lensing=`9`, rotation=`3052`
- delta_chi2 median/min/max: `-7.836931e+05` / `-8.200010e+05` / `-6.907054e+05`
- delta_aic median: `-7.836891e+05`
- delta_bic median: `-7.836770e+05`
- pass fraction (chi2<0, AIC<=-10, BIC<=-10): `1.000000`
- pass all runs: `true`

## Top-Outlier Trim

- Trim fraction: `0.050000`
- Removed rows: lensing=`0`, rotation=`170`
- Kept rows: lensing=`10`, rotation=`3221`
- delta_chi2: `-8.687555e+05`
- delta_aic: `-8.687515e+05`
- delta_bic: `-8.687394e+05`
- trim pass (chi2<0, AIC<=-10, BIC<=-10): `true`
