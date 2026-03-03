# Stability Convergence v6 Lock-In

Date: 2026-03-03  
Status: active contract (official convergence lane)

## What v6 Guarantees

1. Dual-channel decision is explicit:
   - `S2` structural checks must remain hard-pass.
   - `S1` energetic trend is evaluated statistically (Theil-Sen + CI).
2. Promotion evidence is block-based and frozen:
   - `primary`, `attack`, and shifted `holdout` were evaluated.
3. Regression policy is enforced:
   - no missing/extra seed profiles,
   - no pass-rate degradation on official seed-level status fields,
   - block decision must stay `PASS`.

## What v6 Does Not Guarantee (Yet)

1. It is not a full continuum-limit proof.
2. It is not a theorem of convergence for all regimes and all seeds.
3. It does not claim zero positive-slope seeds in every future run.
   - positive-slope fractions are tracked as telemetry alarms (non-blocking for now).

## Telemetry (Yellow-Flag Policy)

- metrics:
  - `positive_full_slope_seed_fraction`
  - `positive_bulk_slope_seed_fraction`
- alarm policy: warning-only (does not fail guard at this stage)
- intent: detect drift early before it becomes a hard regression.

## Change Governance

1. Any definition or threshold change requires a new candidate version (`v7+`) with prereg.
2. Official lane changes require:
   - separate governance switch commit,
   - explicit evidence package,
   - degraded=0 against current official baseline.
