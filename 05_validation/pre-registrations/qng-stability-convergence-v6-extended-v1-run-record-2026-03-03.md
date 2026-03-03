# QNG Stability Convergence v6 Extended Audit v1 - Run Record (2026-03-03)

Status: executed against locked prereg `qng-stability-convergence-v6-extended-v1.md`

## Execution

Output root:

- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/`

Aggregate decision artifacts:

- `block_summary.csv`
- `promotion_report.md`
- `promotion_report.json`
- `manifest.json`
- `run-log.txt`

## Fixed Blocks Executed

1. `primary_s3401_3600` (200 seeds)
2. `attack_s3601_3800` (200 seeds)
3. `holdout_shifted_s3801_4000` (200 seeds, shifted stress grid)

## Result Snapshot

- decision: `PASS`
- block_count: `3`
- `zero_degraded_seed = true`
- `all_v6_blocks_pass = true`
- `holdout_shift_block_pass = true`
- `s2_all_blocks_ok = true`
- `s1_ci_all_blocks_ok = true`
- `total_degraded_seed_count = 0`

Per-block highlights (`legacy -> v6` seed-pass):

- primary: `9/200 -> 186/200` (improved `177`, degraded `0`)
- attack: `7/200 -> 187/200` (improved `180`, degraded `0`)
- shifted holdout: `3/200 -> 148/200` (improved `145`, degraded `0`)

## Runtime

Wall-clock runtime from manifest:

- total: `~7012s` (`~1h57m`)

## Governance Note

No physics formulas or thresholds were changed during this run.
