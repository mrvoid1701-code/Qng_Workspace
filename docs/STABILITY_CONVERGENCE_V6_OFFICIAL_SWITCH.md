# Stability Convergence v6 Official Switch

Date: 2026-03-03  
Status: OFFICIAL (governance switch commit)

## Scope

This switch promotes convergence decision policy `v6` from candidate to official for the stability convergence lane.

## Governance Anchors

- pre-switch tag: `pre-stability-convergence-v6-official`
- post-switch tag: `stability-convergence-v6-official`

## Evidence Basis

Promotion evaluation package:

- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/promotion_report.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/promotion_report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/block_summary.csv`

Frozen checks used for switch:

1. `zero_degraded_seed = true`
2. `all_v6_blocks_pass = true`
3. `holdout_shift_block_pass = true`
4. `s2_all_blocks_ok = true`
5. `s1_ci_all_blocks_ok = true`

## Official Policy Mapping

- Official convergence decision gate: `scripts/tools/run_stability_convergence_gate_v6.py`
- Legacy comparator (diagnostic only): `v5-like` gate (`run_stability_convergence_gate_v4.py` with v5 frozen constants)
- Official decision source report: `report.json -> decision`

## Non-Changes (Anti Post-Hoc)

1. No physics formula edits.
2. No threshold retuning in legacy gates.
3. No seed-list rewrites inside evaluated blocks.

## Known Diagnostic Note

`no_positive_seed_slopes=false` remains tracked as a diagnostic alert in promotion report; it did not block switch because all hard promotion checks remained satisfied.
