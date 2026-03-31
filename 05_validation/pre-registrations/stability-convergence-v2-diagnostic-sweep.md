# Stability Convergence v2 Diagnostic Sweep (Locked, Non-Promotion)

Date locked: 2026-03-03  
Status: LOCKED (diagnostic-only)

## Purpose

Quantify sensitivity of bulk convergence diagnostics to bulk-mask strategy in v2.  
This sweep is explanatory only and cannot be used to promote or retune gate thresholds.

## Fixed Inputs

- source summary:
  - `05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv`
- script:
  - `scripts/tools/run_stability_convergence_v2_diagnostic_sweep_v1.py`

## Fixed Sweep Parameters

- `mask_strategy = active_ratio_quantile`
- `mask_quantiles = {0.00, 0.25, 0.50, 0.75}`
- `bulk_levels = {30, 36, 42}`
- `min_profiles_per_level = 5`
- `metric_field = delta_energy_rel`

## Outputs

- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/bulk_rho_sweep.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/bulk_rho_heatmap.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/report.json`

## Anti Post-Hoc Contract

1. Sweep outputs are diagnostic only and cannot change v2 PASS/FAIL status.
2. Sweep outputs cannot be used to tune any v2 numeric threshold.
3. Any production-policy update must be preregistered separately (`qng-stability-convergence-v3.md` or higher).
