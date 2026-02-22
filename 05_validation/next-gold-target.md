# Next Gold Target Plan

- Updated: `2026-02-20`
- Target domain: `Trajectory REAL`
- Scope owner: `P1/P2 trajectory track`

## Decision

- Next gold candidate is trajectory-real validation (not lensing/rotation).
- This is treated as a cross-domain credibility step after current gold lensing claims.

## Pilot Strategy (Phase 1)

- Use `1-2` pilot mission segments first, not the full mission set.
- Pilot set v1:
- `NEAR_1` (Earth flyby, high-signal pass from DS-005 real).
- `ROSETTA_1` (Earth flyby, moderate-signal pass from DS-005 real).
- Optional cross-check anchor:
- `P10_EQ23` from `data/trajectory/pioneer_ds005_anchor.csv`.

## Pilot Objective

- Reproduce directional signature under the same fixed gating policy.
- Show non-chaotic `tau` behavior across pilot slices.
- Keep baseline-vs-memory comparison on same sample, same sigma, same likelihood.

## Gates (Pilot v1)

- Fit support: `delta_chi2 < 0`, `delta_AIC <= -10`, `delta_BIC <= -10`.
- Directional support and sign-consistency gates fixed in runner.
- Negative controls required:
- orientation shuffle,
- segment shuffle,
- control/symmetric subset behavior.
- Robustness required:
- leave-10%-out,
- top-outlier trim.

## Promotion Policy

- No gold promotion from pilot-only scope.
- Pilot success unlocks full trajectory-real expansion and final gold attempt.

