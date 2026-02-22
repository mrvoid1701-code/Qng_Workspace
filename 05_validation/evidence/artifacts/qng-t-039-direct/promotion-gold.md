# QNG-T-039 Gold Promotion Note (2026-02-17)

Promotion basis for `authenticity=gold`:

1. Primary strict direct-catalog run passes on `MCXC x PSZ2` offsets (`n_lensing=527`) with strong model separation (`delta_chi2 < 0`, `delta_AIC <= -10`).
2. Information criteria remain strong under BIC (`delta_BIC <= -10`) on the same likelihood/sample definition.
3. Primary permutation negative controls pass with wide margin (`lensing_ratio=5.875315e-04`, `rotation_ratio=0.122840`).
4. Leave-10%-out and top-outlier-trim robustness checks pass (`pass_fraction=1.0`, trim gates pass).
5. Separation-threshold robustness sweep passes at `max_sep_arcmin = 3, 4, 5` with all fit gates satisfied.
6. Negative controls pass for each robustness slice (`strict3/strict4/strict5`) with control ratios below registered thresholds.
7. Independent direct-catalog anchor replication (`MCXC x SPT`) passes fit gates and negative controls.
8. Leakage risk remains `low`; promotion removes prior proxy-dominated silver blocker.

Primary artifacts:

- `05_validation/evidence/artifacts/qng-t-039-direct/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-direct/model-comparison.md`
- `05_validation/evidence/artifacts/qng-t-039-direct/robustness-checks.md`
- `05_validation/evidence/artifacts/qng-t-039-direct/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict3/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict4/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict4/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict5/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-psz2-strict5/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-spt-anchor/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-039-spt-anchor/negative-controls-summary.csv`
