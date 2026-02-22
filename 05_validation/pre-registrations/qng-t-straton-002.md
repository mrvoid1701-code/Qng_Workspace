# Pre-registration: QNG-T-STRATON-002

- Authored by: Claude Sonnet 4.6 (2026-02-22)
- Claim: `QNG-C-014` (tau depends on chi; straton relevance)
- Hypothesis: tau scales with spacecraft mass (tau_i = alpha * m_i) rather than a single global tau.
- Version: v2 — classic subset only (published residuals, no placeholders).
- Supersedes: v1 fail reason — placeholder residuals for JUNO_1, BEPICOLOMBO_1, SOLAR_ORBITER_1
  inflated alpha variance (CV=0.775). This version excludes those missions.

## Dataset

- Source: `DS-005` derived flyby file + `data/trajectory/flyby_ds005_real.csv`.
- Classic subset (n=13 rows, 7 missions): all must have published OD residuals and σ.

```
CLASSIC_PASS_IDS = {
  GALILEO_1, GALILEO_2,     # Galileo   (2223 kg)
  NEAR_1,                   # NEAR      (805 kg)
  CASSINI_1,                # Cassini   (5600 kg)
  ROSETTA_1, ROSETTA_2, ROSETTA_3,  # Rosetta (3000 kg)
  MESSENGER_1,              # Messenger (1107 kg)
  EPOXI_1, EPOXI_2, EPOXI_3, EPOXI_4, EPOXI_5  # EPOXI (650 kg)
}
```

- Pioneer rows (P10_EQ23, P11_EQ24, P10P11_FINAL) excluded: different physical feature type.
- Placeholder residuals (JUNO_1, BEPICOLOMBO_1, SOLAR_ORBITER_1) excluded.

## Models

- Model A (null): a_pred_i = tau0 * feature_i  (k=1, tau0 global constant)
- Model B (straton linear): a_pred_i = alpha * m_i * feature_i  (k=1, linear mass scaling)
- Model C (straton power law): a_pred_i = alpha * m_i^beta * feature_i  (k=2, diagnostic only)

All three are single-pass weighted least squares.
Feature: `feature_base_m_s3`. Observed: `a_obs_whole_m_s2`.
Weights: 1/sigma^2, sigma = sigma_whole_m_s2 (fallback sigma_perigee if zero, then 1e-18).

## Gates (apply to Model B on classic subset)

1. delta_bic(B-A) = bic_B - bic_A <= -10 (strong support for mass-scaling).
2. alpha stability: CV_bootstrap(alpha) < 0.30.
3. Negative control (shuffle masses): median delta_bic_shuffle > -2 (signal collapses).
4. Exact leave-one-row-out (LOO): pass_fraction across all 13 individual LOO fits >= 0.90
   (i.e., at least 12 of 13 LOO fits must satisfy delta_bic_loo <= -10).

Pass only if all four gates are true. Do not retune thresholds after running.

## Mandatory Diagnostics (not gates — required outputs for paper defensibility)

D1. Leave-one-row-out influence table (all 13 fits):
    - columns: pass_id, mission_id, mass_kg, alpha_full, alpha_loo, delta_alpha,
      delta_alpha_rel_pct, delta_bic_loo, delta_ll_loo, gate_pass
    - Purpose: identify leverage rows. If 1–2 rows drive the result, note explicitly.

D2. Leave-one-mission-out influence table (7 mission groups):
    - columns: mission_id, n_rows_dropped, alpha_full, alpha_loo, delta_alpha,
      delta_alpha_rel_pct, delta_bic_loo, delta_ll_loo, gate_pass
    - Purpose: identify leverage missions.

D3. Model C power-law fit (diagnostic, no pass/fail gate):
    - Grid search beta in [0.10, 3.00] step 0.05 (locked reference).
    - Ternary search continuous cross-check (same range, tol=1e-6) — must agree with grid within 0.10.
    - Report: best_beta_grid, best_beta_continuous, LL, BIC(k=2), delta_bic(C-A), delta_bic(C-B).
    - Bootstrap 95% CI on beta (500 resamples, seed 20260228).
    - BIC penalty for k=2 vs k=1: ln(n) = ln(13) ≈ 2.565 (must be stated explicitly).
    - If delta_bic(C-B) < -2: note power law preferred (informational only — not a gate).

D4. Residuals diagnostic (per-row, both models):
    - columns: pass_id, mission_id, mass_kg, sigma, a_obs,
      residual_A, residual_B, std_residual_A, std_residual_B, leverage_flag (|std_resid_B| > 2)
    - Purpose: std_residual vs mass reveals if ΔBIC is real or driven by 1–2 outlier rows.
    - Required: sigma summary (min/median/max) explicitly stated in evidence.

D5. Full BIC decomposition (separate CSV):
    - columns: model, k, n, LL, BIC, chi2, param, param_name
    - Both Model A and Model B; delta row included.
    - Purpose: confirm ΔBIC is not inflated by arbitrary sigma (confirmed clean in v2 since
      placeholder missions are excluded; sigma summary provides transparency).

## Controls

- Mass shuffle (permute spacecraft_mass_kg across classic rows, seed 20260227).
- Include all classic rows (no control-only exclusion for this test).

## Fixed

- Classic subset definition (listed above — locked, no additions after viewing results).
- Feature column: `feature_base_m_s3`.
- Observed acceleration: `a_obs_whole_m_s2`.
- Sigma fallback chain: sigma_whole → sigma_perigee → 1e-18.
- Single-parameter fits for Model A and B (k=1 each).
- Two-parameter fit for Model C (k=2).
- Random seeds: bootstrap 20260225, leaveout 20260226 (unused — replaced by exact LOO),
  shuffle 20260227, model-c-bootstrap 20260228.

## Free

- Bootstrap resamples: ≥ 400 (can increase, not decrease).
- Model C beta grid resolution: ≤ 0.05 step (can increase, not decrease).
- Output format: CSV + Markdown report.

## Outputs

- `fit-summary.csv`               (gates + core metrics + sigma summary)
- `bic-decomposition.csv`         (n, k, LL, BIC, chi2 per model — D5)
- `residuals-diagnostic.csv`      (per-row residual + std_residual vs mass — D4)
- `loo-row-influence.csv`         (D1)
- `loo-mission-influence.csv`     (D2)
- `model-c-report.csv`            (D3: grid + continuous + CI)
- `model-c-grid.csv`              (full beta grid)
- `bootstrap-alpha.csv`
- `bootstrap-beta-modelc.csv`
- `negative-controls-summary.csv`
- `straton-002-report.md`
- `run-log.txt`

## Pass/Fail

- Pass: all four gates true.
- Fail: any gate false; do not retune thresholds post-run.
- If gate 2 (alpha CV) fails but gate 4 (LOO) passes with pass_fraction = 1.0:
  record as "fail with note — high variance may be mass-range artifact" and plan v3.
