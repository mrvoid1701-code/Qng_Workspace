# QNG Research Note: GR-QM Governance Closure + Stability Stress Snapshot (v2)

Date: 2026-03-04

## Abstract

This note records a governance-focused closure sprint on the QNG codebase. The main outcome is operational: GR Stage-3 and QM Stage-1 were both advanced through candidate-to-official policy updates under non-degradation checks, while coupling backbone and stress stability evidence were refreshed without threshold/formula edits.

## 1. GR Stage-3 Closure

The G11 candidate-v5 policy was evaluated on prereg blocks:

- primary (`DS-002/003/006`, `3401..3600`): `597/600 -> 600/600`
- attack (`DS-002/003/006`, `3601..4100`): `1433/1500 -> 1459/1500`
- holdout (`DS-004/008`, `3401..3600`): `398/400 -> 400/400`

All three blocks satisfied `degraded=0`. The governance mapping was applied as official Stage-3 v5 (`gr-stage3-g11-v5-official`) and protected by a refreshed Stage-3 baseline guard (`PASS`).

## 2. QM Stage-1 Strengthening

The G17 candidate-v3 generalized local-gap policy was evaluated on prereg blocks:

- primary lane: `411/600 -> 513/600`
- attack lane: `1017/1500 -> 1255/1500`
- holdout lane: `322/400 -> 360/400`

Again, `degraded=0` held across all blocks. Governance mapping was applied as official Stage-1 v4 (`qm-stage1-g17-v3-official`), with baseline guard re-check (`PASS`).

Post-switch Stage-1 taxonomy on `2500` profiles reports `372` fails (`14.88%`), still dominated by `G18`, not by coupling closure.

## 3. Coupling Backbone Status

The QM-GR coupling audit v2 bundle remains stable:

- completed profiles: `2500/2500`
- `G20`: `2500/2500` pass
- GR guard pre/post: `PASS`

This run was compute-heavy (`~5h` wall-clock), and remains the backbone evidence that QM lane activation does not regress frozen GR behavior in the tested regime.

## 4. Stability Stress Snapshot

Additional requested packs were executed:

- dual stability sweep
- chi-sigma phase diagram
- scaling test with convergence v6 gate
- perturbation torture test
- long emergence run

Observed pattern: structural constraints stay robust, while energy-drift remains the dominant limiter under strong perturbation and long-time runs. This aligns with the existing dual-channel interpretation (structural vs energetic lane).

## 5. Methodology Guard

This sprint intentionally avoided post-hoc threshold retuning:

1. no gate formula changes,
2. no threshold edits,
3. candidate promotion only via prereg blocks + `degraded=0`,
4. baseline/guard updates after governance switch.

## Conclusion

The repository moved from partial closure to stronger frozen governance:

- GR Stage-3 primary is now `600/600` under official-v5 mapping.
- QM Stage-1 official policy is upgraded to G17-v3 with stronger lane pass rates.
- Coupling backbone remains stable on full `2500` profile bundle.

The next high-impact lane remains QM Stage-2 gate hardening (dominant `G18` signatures) while preserving the frozen GR/QM guardrails.
