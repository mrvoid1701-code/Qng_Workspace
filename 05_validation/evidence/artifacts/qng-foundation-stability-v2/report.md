# QNG EL Consistency Report (v1)

- generated_utc: `2026-03-06T00:34:32.766997+00:00`
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

- This checker measures residual `R = U_current - U_EL` using two independent one-step implementations.
- `global_abs_*` uses per-node-step joint residual `max(|R_sigma|, |R_chi|, |R_phi|)` (not channel concatenation).
- Non-zero Sigma residual is dominated by bounded projection (`clip`) needed to enforce `Sigma in [0,1]`.
- chi/phi residuals are expected near machine-zero when implementations are consistent.
