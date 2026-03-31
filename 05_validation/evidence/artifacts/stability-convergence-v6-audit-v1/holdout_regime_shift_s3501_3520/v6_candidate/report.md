# Stability Convergence Gate v6

- generated_utc: `2026-03-03T15:19:37.230066+00:00`
- summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/raw/summary.csv`
- prereg_doc: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/pre-registrations/qng-stability-convergence-v6.md`
- seed_count: `20`
- decision: `PASS`

## S2 Structural Lane

- s2_seed_pass_fraction: `1.000000` (must be `1.0`)
- bulk_valid_seed_fraction: `1.000000` (must be `1.0`)

## S1 Energetic Lane (Theil-Sen + CI)

- full_slope_median: `-0.000606222`
- full_slope_ci: `[-0.000765830, -0.000420028]` (require upper `< 0`)
- bulk_slope_median: `-0.000712583`
- bulk_slope_ci: `[-0.001223208, -0.000372375]` (require upper `< 0`)

## Rule Results

- s2_all_seeds_pass_ok: `true`
- bulk_valid_all_seeds_ok: `true`
- s1_full_slope_ci_excludes_zero_neg_ok: `true`
- s1_bulk_slope_ci_excludes_zero_neg_ok: `true`
