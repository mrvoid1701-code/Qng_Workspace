# G16b Definition Change Proposal (Candidate-Only)

Date: 2026-03-01

## Current Status

- Official gate logic remains unchanged.
- `G16b` currently uses global linear fit quality: `R²(G11, 8πG T11) > 0.05`.
- This document proposes a **candidate** diagnostic upgrade only (`G16b-v2`), not an immediate replacement.

## Why v1 Is Fragile

- A single global `R²` can under-represent coupling when:
  - stress signal is low or sign-mixed (`T11` near-zero dominated),
  - relation is monotonic but not strongly linear,
  - high-signal subset behaves differently from the full set.
- In the current 60-profile grid, all `G16` failures are `G16b`-only failures.

## v2 Candidate Diagnostics (No Gate Switch Yet)

Candidate package to track per profile:

- `mean/std` for `T11` and `G11`
- sign fractions for `T11`: positive / negative / near-zero
- signal dominance ratio: `std(T11) / |mean(T11)|`
- Pearson `r(T11, G11)`
- Spearman `ρ(T11, G11)`
- high-signal subset diagnostics (top 20% `|T11|`):
  - `R²_high_signal`
  - `Pearson_high_signal`
  - `Spearman_high_signal`

These are diagnostics, not official thresholds in this commit.

## A/B Diagnosis Framing

- Axis A: `T11` discretization/noise issue
  - e.g. low-signal or sign-cancelled stress proxy.
- Axis B: geometric/matter operator compatibility issue
  - e.g. monotonic relation but weak global linear fit.

Taxonomy output maps each failing profile to a provisional A/B issue axis.

## Promotion Rule (Pre-Registered)

`G16b-v2` can be promoted from candidate to official decision gate only if all are met:

1. Fixed protocol is frozen before reruns (datasets, seeds, metrics, thresholds if any).
2. Evaluation grid minimum: `DS-002/DS-003/DS-006` × `200 seeds` each.
3. Results are stable across reruns without changing formulas or thresholds.
4. Legacy `G16b-v1` remains reported in parallel for one release cycle.

Until then:

- `G16b-v1` remains official.
- `G16b-v2` remains candidate diagnostic only.

