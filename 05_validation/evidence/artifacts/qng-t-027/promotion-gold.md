# QNG-T-027 Gold Promotion Note (2026-02-16)

Promotion basis for `authenticity=gold`:

1. Strict direct-catalog baseline passes (`MCXC x PSZ2`, `n_lensing=527`, strict ID-separation gate enabled).
2. Information criteria remain strong across AIC and BIC (`delta_AIC <= -10`, `delta_BIC <= -10`).
3. Separation-threshold robustness sweep passes at `max_sep_arcmin = 3, 4, 5`.
4. Leave-10%-out and top-outlier-trim checks pass without sign flips.
5. Independent direct-catalog anchor replication passes on `MCXC x SPT` matching.
6. Permutation negative controls pass on both baseline and robustness subsets.
7. Leakage risk remains `low` with no detected control leakage above registered thresholds.

Primary artifacts:

- `05_validation/evidence/artifacts/qng-t-027/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027/model-comparison.md`
- `05_validation/evidence/artifacts/qng-t-027/robustness-checks.md`
- `05_validation/evidence/artifacts/qng-t-027/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027-psz2-strict3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027-psz2-strict4/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027-psz2-strict5/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027-spt-anchor/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-027-spt-anchor/negative-controls-summary.csv`
