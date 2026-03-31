# Stability Convergence v4 Failure Taxonomy (v1)

- generated_utc: `2026-03-03T14:16:41.897823+00:00`
- seed_total: `20`
- bulk_fail_seed_count: `17`
- bulk_fail_rate: `0.850000`

## Dominant Findings

- CI non-exclusion dominates failures: `17/17` fail seeds have `tau_ci_high >= 0`.
- ties/discreteness contribution: `0/17` fail seeds show at least one adjacent tie in bulk medians.
- support collapse signal (below min profiles): `0/17`.

## Reason Flags (fail seeds)

- `ci_not_excluding_zero`: `17`

## Interpretation

- v4 failures are primarily a statistical-power issue (CI width/discreteness) rather than threshold tuning failure.
- bulk support is present (`support_ok`) but with only a few bulk levels, CI on trend remains broad.
