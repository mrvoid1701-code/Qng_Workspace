# QM Stage-1 Freeze (Internal Release)

Date: 2026-03-05  
Stage ID: `QM-Stage-1`  
Release type: internal freeze

## Scope

`QM-Stage-1` covers QM lane decision behavior through gates `G17..G20`.

Frozen official policy:

- `G17 official`: `G17a-v4 + G17b-v6` (high-signal median recovery on legacy fail-cases)
- `G18 official`: `G18d-v7 + G18b-v8` (local-ds + robust trimmed n*IPR decision layer)
- `G19 official`: `G19-v2` (`G19d-v2` high-signal slope envelope)
- `G17-v1` and `G18-v1`: legacy diagnostic-only
- `G20`: inherited unchanged in official-v13 policy outputs

## Guarantees

This freeze guarantees:

1. Reproducible official QM Stage-1 outputs via the frozen `official-v13` policy.
2. Baseline + regression guard coverage with `PASS` on:
   - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v11/latest_check/`
3. QM-GR coupling audit v2 operational stability:
   - primary (`600/600`) PASS
   - attack (`1500/1500`) PASS
   - holdout (`400/400`) PASS
   - `G20` pass-rate `2500/2500`
   - GR guard pre/post all chunks `PASS`

## Explicit Non-Claims

This freeze does not claim:

1. QM Stage-2 formal closure,
2. bounded-stability proof as formal theorem,
3. variational-derivation completeness for all future coupled updates.

Those remain in `candidate/prereg` lanes and are promoted only after preregistered evaluation with non-degradation checks.

## Governance Policy

Any change to `QM-Stage-1` official policy must run as candidate lane first, with:

1. preregistered datasets/seeds/protocol,
2. primary + attack + holdout evaluation,
3. `degraded=0` versus current official policy,
4. coupling audit and regression guard re-checks.

## Freeze Pointers

- lane policy: `docs/QM_LANE_POLICY.md`
- gate map: `docs/GATES.md`
- official switch records:
  - `docs/QM_STAGE1_G17_V2_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V2_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G17_V3_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V3_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G17B_V4_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V4_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V5_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V6_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G17A_V4_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18_V7_G19_V2_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G17B_V6_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G18B_V8_OFFICIAL_SWITCH.md`
- baseline guard doc: `docs/QM_STAGE1_BASELINE_GUARD.md`
- reproducibility commands: `docs/REPRODUCIBILITY.md`

## Release Tag

Internal freeze tag: `qm-stage1-g18b-v8-official`
