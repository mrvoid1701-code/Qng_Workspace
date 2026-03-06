# D4 v6 Forensics v1

- exploratory only: no promotion, no threshold changes
- generated_utc: `2026-03-06T15:22:15.432371+00:00`
- decision: `NO_STRONG_COLLAPSE_SIGNAL`

## Core Signals

- high |corr(H1,outer)| rate (>=0.98): `0.000000`
- median |corr(H1,outer)|: `0.810953`
- p90 |corr(H1,outer)|: `0.866746`
- median cond(X^T X): `53.661583`
- p90 cond(X^T X): `76.701276`
- infinite-cond count: `0`
- boundary-hit rate (any): `1.000000`
- single-component-only rate: `1.000000`

## Interpretation

- no strong collapse signature under current heuristic; inspect surfaces directly

## Artifacts

- `objective_surface.csv`
- `identifiability_surface.csv`
- `boundary_hits.csv`
- `boundary_hit_summary.csv`
- `active_components.csv`
