# QNG Stability V1 Strict - Pre-registration

- Date locked: 2026-03-03
- Status: LOCKED
- Policy ID: `qng-stability-v1-strict`
- Freeze references:
  - `docs/STABILITY_V1_STRICT.md`
  - `03_math/derivations/qng-stability-action-v1.md`
  - `03_math/derivations/qng-stability-update-v1.md`

## Purpose

Lock a reproducible stress protocol for the stability term (`Sigma`) and its coupled variables (`chi`, `phi`) without post-hoc threshold edits.

## Fixed Runner

```text
python scripts/tools/run_stability_stress_v1.py
```

Default sweep grid:

- `edge_prob in {0.08, 0.18, 0.32}`
- `chi_scale in {0.50, 1.00, 1.50}`
- `noise_level in {0.00, 0.01, 0.03}`
- `phi_shock in {0.00, 0.40}`

Total default cases: `54`.

## Locked Gates

1. `gate_sigma_bounds`: `Sigma in [0,1]`
2. `gate_metric_positive`: `min(g_diag) > 0`
3. `gate_metric_cond`: `max cond(g_diag) <= 3.0`
4. `gate_runaway`: `max |chi| <= 6.0`
5. `gate_energy_drift`: `|delta_E / E| <= 0.90`
6. `gate_variational_residual`: `max_residual <= 0.60`
7. `gate_alpha_drift`: `max |delta alpha / alpha| <= 0.05` evaluated only on nodes with `|chi| >= 0.05`
8. `gate_no_signalling`: `max_nonlocal_delta <= 1e-9`

Overall case pass:

```text
all_pass = logical_and(all gate passes)
```

## Required Artifacts

Output folder:

```text
05_validation/evidence/artifacts/stability-v1/
```

Required files:

- `summary.csv`
- `gate_summary.csv`
- `report.md`
- `manifest.json`
- `run-log.txt`

## Anti Post-Hoc Policy

1. No threshold change after observing run results.
2. Any threshold/equation update requires:
   - new prereg version (`...-v2.md`)
   - new output folder/version
   - explicit degrade/non-degrade comparison vs v1 strict.
