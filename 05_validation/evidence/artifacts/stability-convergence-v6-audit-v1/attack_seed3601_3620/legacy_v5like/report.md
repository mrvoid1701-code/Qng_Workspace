# Stability Convergence Gate v4

- generated_utc: `2026-03-03T15:16:02.972391+00:00`
- summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/raw/summary.csv`
- prereg_doc: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/pre-registrations/qng-stability-convergence-v5.md`
- seed_count: `20`
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

- full_seed_pass_fraction: `0.450000` (min `0.85`)
- bulk_seed_pass_fraction: `0.050000` (min `0.85`)
- bulk_ci_pass_fraction: `0.200000`
- rho_full_median: `-0.803571` (max `-0.6`)
- tau_bulk_median: `-0.600000`
- tau_bulk_ci_high_median: `0.200000` (must be `< 0`)

## Rule Results

- full_seed_pass_fraction_ok: `false`
- bulk_seed_pass_fraction_ok: `false`
- rho_full_median_ok: `true`
- tau_bulk_ci_high_median_ok: `false`
