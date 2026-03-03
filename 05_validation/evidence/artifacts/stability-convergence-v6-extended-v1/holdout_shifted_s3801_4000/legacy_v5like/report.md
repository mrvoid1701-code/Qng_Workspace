# Stability Convergence Gate v4

- generated_utc: `2026-03-03T17:43:13.239404+00:00`
- summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/holdout_shifted_s3801_4000/raw/summary.csv`
- prereg_doc: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/pre-registrations/qng-stability-convergence-v5.md`
- seed_count: `200`
- decision: `FAIL`

## Bulk Trend Estimator

- estimator: `Kendall tau` over bulk-level medians
- uncertainty: bootstrap CI on tau; pass requires `tau_ci_high < 0`
- bootstrap_reps: `400`
- ci_alpha: `0.05`

## Bulk Support Policy

- min profiles per bulk level: `5`
- core stable size min: `6`
- core stable ratio min: `0.1`
- insufficient bulk support seed count: `0`

## Aggregate Checks

- full_seed_pass_fraction: `0.495000` (min `0.85`)
- bulk_seed_pass_fraction: `0.050000` (min `0.85`)
- bulk_ci_pass_fraction: `0.050000`
- rho_full_median: `-0.800000` (max `-0.6`)
- tau_bulk_median: `-1.000000`
- tau_bulk_ci_high_median: `1.000000` (must be `< 0`)

## Rule Results

- full_seed_pass_fraction_ok: `false`
- bulk_seed_pass_fraction_ok: `false`
- rho_full_median_ok: `true`
- tau_bulk_ci_high_median_ok: `false`
