# QM Stage-1 Regression Guard Report (v1)

- generated_utc: `2026-03-04T09:30:12.459605Z`
- decision: `PASS`

## Block Summary

### primary
- decision: `PASS`
- profiles_expected/observed: `600/600`
- profiles_missing: `0`
- profiles_extra: `0`
- official_fields_degraded: `0`
- status_mismatches: `0`

### attack
- decision: `PASS`
- profiles_expected/observed: `1500/1500`
- profiles_missing: `0`
- profiles_extra: `0`
- official_fields_degraded: `0`
- status_mismatches: `0`

### holdout
- decision: `PASS`
- profiles_expected/observed: `400/400`
- profiles_missing: `0`
- profiles_extra: `0`
- official_fields_degraded: `0`
- status_mismatches: `0`

## Failure Criteria

- FAIL if any expected `(dataset_id, seed)` profile is missing.
- FAIL if any extra `(dataset_id, seed)` profile appears.
- FAIL if any official gate pass rate decreases vs baseline.

