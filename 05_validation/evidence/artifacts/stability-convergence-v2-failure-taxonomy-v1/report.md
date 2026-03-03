# Stability Convergence V2 Failure Taxonomy (v1)

- generated_utc: `2026-03-03T09:21:36.800866+00:00`
- source_report: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/report.json`
- source_seed_checks: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv`
- source_raw_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv`
- convergence_decision: `FAIL`
- seed_count: `20`
- bulk_fail_seed_count: `10`

## Dominant Fail Mode

- bulk_vs_full median delta step fraction (`full-bulk`): `0.000000`
- fail-mode distribution: `{'pass': 10, 'bulk_only_fail': 8, 'full_and_bulk_fail': 2}`

## Top 3 Hypothesized Causes

- conditioning-related metrics rise in failing seeds (delta fail-pass `-0.000`), suggesting operator sensitivity in bulk subset.
- residual-related metrics rise in failing seeds (delta fail-pass `0.000`), implying numerical/stochastic contamination of bulk slope.
- additional cause requires richer per-node observables (multi-peak and topology-local diagnostics not present in v2 summary).

## Data Availability Notes

- multi-peak flag is not directly available in stability convergence summaries.
- `phi_shock_rate` is used as a mixing proxy for diagnostics only.
