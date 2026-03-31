# Stability Convergence Gate v6

- generated_utc: `2026-03-03T17:11:19.912199+00:00`
- summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/attack_s3601_3800/raw/summary.csv`
- prereg_doc: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/pre-registrations/qng-stability-convergence-v6.md`
- seed_count: `200`
- decision: `PASS`

## S2 Structural Lane

- s2_seed_pass_fraction: `1.000000` (must be `1.0`)
- bulk_valid_seed_fraction: `1.000000` (must be `1.0`)

## S1 Energetic Lane (Theil-Sen + CI)

- full_slope_median: `-0.000529750`
- full_slope_ci: `[-0.000561841, -0.000481083]` (require upper `< 0`)
- bulk_slope_median: `-0.000499190`
- bulk_slope_ci: `[-0.000565412, -0.000434375]` (require upper `< 0`)

## Rule Results

- s2_all_seeds_pass_ok: `true`
- bulk_valid_all_seeds_ok: `true`
- s1_full_slope_ci_excludes_zero_neg_ok: `true`
- s1_bulk_slope_ci_excludes_zero_neg_ok: `true`
