# QNG Stability Convergence Contract v6 (Candidate)

Date locked: 2026-03-03  
Status: LOCKED (candidate run executed; governance switch pending)

## Purpose

Adopt dual-channel convergence governance:

- `S2` structural lane stays deterministic and hard-gated.
- `S1` energetic lane is treated as a statistical trend problem.

## Single Conceptual Change (Locked)

Only one conceptual change is introduced vs v5:

- S1 decision moves from strict per-seed pass semantics to block-level statistical evidence on robust slope/trend.

Everything else remains fixed.

## Fixed Data Block

- same seed block: `3401..3420`
- same stress grid family as convergence lane (`steps=60`, prereg-controlled node levels)
- S2 gate set unchanged

## S2 Structural Rule (Unchanged)

S2 remains hard deterministic:

- structural gates are evaluated exactly as defined in prior stability contracts.
- S2 failure is immediate fail.

## S1 Energetic Rule (New Statistical Form)

For each seed, compute robust trend summaries on bulk/full levels:

- Theil-Sen slope (primary sign metric)
- Kendall tau with bootstrap CI (support metric)

Block-level S1 decision uses:

1. median Theil-Sen slope across seeds `< 0`
2. bootstrap CI of median slope excludes `0` on upper bound
3. supporting Kendall summary reported (not primary decision rule)

No numeric threshold from prior gates is reduced or relaxed; decision semantics are statistical aggregation.

## Locked Constraints

1. No edits to S2 gate formulas/thresholds.
2. No seed-list edits post-lock.
3. No tuning using v6 results; any change requires `v7`.

## Anti Post-Hoc

1. v6 is candidate-only until run record exists.
2. Report must include side-by-side S1 and S2 outcomes.
3. Promotion requires explicit governance switch commit.
