# QNG Stability Stress Report (v1)

- generated_utc: `2026-03-03T17:43:09.814716+00:00`
- cases_total: `43200`
- all_pass: `18700/43200`
- all_fail: `24500/43200`
- mean gate energy drift (`|delta_E/E|`): `0.904728`
- mean Noether-like drift (`|delta_E_noether/E_noether|`): `0.071959`

## Locked Gate Thresholds

- `max_abs_chi <= 6.0`
- `metric_cond_max_seen <= 3.0`
- `|delta_E/E| <= 0.9`
- `max_residual <= 0.6`
- `max |delta_alpha/alpha| <= 0.05` for `|chi| >= 0.05`
- `max_nonlocal_delta <= 1e-09`

## Gate Pass Rates

- `gate_sigma_bounds`: `43200/43200` (pass_rate=1.000000)
- `gate_metric_positive`: `43200/43200` (pass_rate=1.000000)
- `gate_metric_cond`: `43200/43200` (pass_rate=1.000000)
- `gate_runaway`: `43200/43200` (pass_rate=1.000000)
- `gate_energy_drift`: `18700/43200` (pass_rate=0.432870)
- `gate_variational_residual`: `43200/43200` (pass_rate=1.000000)
- `gate_alpha_drift`: `43200/43200` (pass_rate=1.000000)
- `gate_no_signalling`: `43200/43200` (pass_rate=1.000000)
- `all_pass`: `18700/43200` (pass_rate=0.432870)
