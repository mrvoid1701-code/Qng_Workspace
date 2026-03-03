# Stability Convergence V2 Failure Taxonomy (v1)

- generated_utc: `2026-03-03T12:26:15.644119+00:00`
- source_report: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/report.json`
- source_seed_checks: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv`
- source_level_stats: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/level_stats.csv`
- source_step_checks: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/step_checks.csv`
- source_raw_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv`
- convergence_decision: `FAIL`
- seed_count: `20`
- bulk_fail_seed_count: `10`

## Bulk Fail Definition

- a seed is `bulk fail` iff `bulk_pass=false` in `seed_checks.csv`.
- bulk levels are `[30, 36, 42]` and full levels are `[24, 30, 36, 42, 48]`.
- fail localization uses `step_checks.csv` transitions and `level_stats.csv` medians.

## Dominant Fail Mode

- bulk_vs_full median delta step fraction (`full-bulk`): `0.000000`
- fail-mode distribution: `{'pass': 10, 'bulk_only_fail': 8, 'full_and_bulk_fail': 2}`
- failing transitions (bulk scope): `{'30->36': 7, '36->42': 1}`
- failing transitions (full scope, fail seeds): `{'30->36': 7, '42->48': 2, '36->42': 1}`

## Top 3 Hypothesized Causes

- dominant fail class is bulk-specific (`bulk_only_fail=8` vs `full_and_bulk_fail=2`), indicating the failure concentrates in bulk scoring rather than full-scale convergence.
- bulk transition failures concentrate on `{'30->36': 7, '36->42': 1}`; this localizes where the monotonic trend breaks inside bulk levels.
- only `2` seeds fail both full and bulk, so global continuum trend is mostly intact while bulk-level estimator remains fragile.

## Data Availability Notes

- multi-peak flag is not directly available in stability convergence summaries.
- `phi_shock_rate` is used as a mixing proxy for diagnostics only.
