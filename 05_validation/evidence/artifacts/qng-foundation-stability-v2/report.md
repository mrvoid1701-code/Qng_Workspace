# QNG EL Consistency Report (v2)

- generated_utc: `2026-03-06T00:44:42.903652+00:00`
- comparator_mode: `v2`
- profiles_total: `432`
- profiles_pass: `432`
- profiles_fail: `0`

## Locked Thresholds

- `sigma_abs_median <= 0.02`
- `sigma_abs_p90 <= 0.03`
- `sigma_abs_max <= 0.06`
- `global_abs_p90 <= 0.03`
- `global_abs_max <= 0.06`
- `chi_abs_max <= 1e-10`
- `phi_abs_max <= 1e-10`

## Dataset Summary

- `STABILITY-ATTACK`: pass `162/162` (rate=1.000000), sigma_p90_med=0.000000, global_max_max=0.000000, all_pass=pass
- `STABILITY-HOLDOUT`: pass `108/108` (rate=1.000000), sigma_p90_med=0.000000, global_max_max=0.000000, all_pass=pass
- `STABILITY-PRIMARY`: pass `162/162` (rate=1.000000), sigma_p90_med=0.000000, global_max_max=0.000000, all_pass=pass
- `ALL`: pass `432/432` (rate=1.000000), sigma_p90_med=0.000000, global_max_max=0.000000, all_pass=pass

## Interpretation

- `v2` mode: residual `R = U_current - U_EL` using two one-step implementations.
- `v1` mode: legacy self-check behavior (kept for historical reproducibility).
- `v2` global metric uses joint residual `max(|R_sigma|, |R_chi|, |R_phi|)`.
- `v1` global metric preserves legacy concatenation behavior.
