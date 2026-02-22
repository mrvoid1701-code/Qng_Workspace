# Evidence - QNG-T-STRATON-002

- Priority: P2
- Claim: `QNG-C-014` — tau scales with spacecraft mass (straton mass-scaling)
- Pre-registration: `05_validation/pre-registrations/qng-t-straton-002.md`
- Status: pending (not yet run)
- Authored by: Claude Sonnet 4.6 (2026-02-22)
- Note: v2 of QNG-T-STRATON-001 (fail). Root cause fixed: placeholder residuals for JUNO_1,
  BEPICOLOMBO_1, SOLAR_ORBITER_1 excluded. Classic subset only (n=13 rows, 7 missions).

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_straton_002.py
```

Optional flags:
```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_straton_002.py `
  --bootstrap-runs 400 `
  --shuffle-runs 400 `
  --modelc-bootstrap-runs 500 `
  --out-dir 05_validation/evidence/artifacts/qng-t-straton-002
```

## BIC Decomposition (fill after execution)

| Model | k | n | LL | BIC | chi2 | param |
| --- | --- | --- | --- | --- | --- | --- |
| A (null) | 1 | TBD | TBD | TBD | TBD | tau_const=TBD |
| B (straton) | 1 | TBD | TBD | TBD | TBD | alpha=TBD |
| delta (B-A) | - | - | TBD | TBD | TBD | - |

## Sigma Summary (fill after execution)

| min | median | max |
| --- | --- | --- |
| TBD | TBD | TBD |

## Key Metrics (fill after execution)

| Metric | Value | Gate | Status |
| --- | --- | --- | --- |
| `n_classic_rows` | TBD | info | - |
| `delta_bic (B-A)` | TBD | `<= -10` | - |
| `alpha` | TBD | info | - |
| `alpha_cv_bootstrap` | TBD | `< 0.30` | - |
| `shuffle_delta_bic_median` | TBD | `> -2.0` | - |
| `loo_pass_fraction` | TBD (X/13) | `>= 0.90` | - |
| `model_c_best_beta_grid` | TBD | diagnostic | - |
| `model_c_best_beta_continuous` | TBD | diagnostic | - |
| `model_c_delta_bic_c_vs_b` | TBD | diagnostic | - |
| `beta_95_ci` | TBD | diagnostic | - |

## Residuals Diagnostic D4 (fill after execution)

| pass_id | mass_kg | sigma | std_resid_A | std_resid_B | leverage |
| --- | --- | --- | --- | --- | --- |
| TBD | | | | | |

## Influence Diagnostics (fill after execution)

### Leave-one-row-out D1

| pass_id | mission_id | mass_kg | delta_alpha_rel_pct | delta_bic_loo | gate |
| --- | --- | --- | --- | --- | --- |
| TBD | | | | | |

### Leave-one-mission-out D2

| mission_id | n_rows | delta_alpha_rel_pct | delta_bic_loo | gate |
| --- | --- | --- | --- | --- |
| TBD | | | | |

## Artifacts

- `05_validation/evidence/artifacts/qng-t-straton-002/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/loo-row-influence.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/loo-mission-influence.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/model-c-report.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/model-c-grid.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/bootstrap-alpha.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/bootstrap-beta-modelc.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/negative-controls-summary.csv`
- `05_validation/evidence/artifacts/qng-t-straton-002/straton-002-report.md`
- `05_validation/evidence/artifacts/qng-t-straton-002/run-log.txt`

## Decision

- Decision: pending
- Rationale: (fill after execution)

## v1 Comparison

| | STRATON-001 (fail) | STRATON-002 (pending) |
| --- | --- | --- |
| Dataset | Full DS-005 (19 rows) | Classic subset (13 rows) |
| Placeholder missions | JUNO_1, BEPI, SO included | Excluded |
| alpha CV | 0.775 (FAIL) | TBD |
| LOO fraction | 0.886 (FAIL) | TBD (exact LOO) |
| delta_bic | -3151.88 (PASS) | TBD |
| Model C | not tested | grid search + CI |
