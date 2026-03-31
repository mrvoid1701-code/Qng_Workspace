# QM Stage-2 Failure Taxonomy Post-v6 (v1)

- generated_utc: `2026-03-05T07:55:32.559448+00:00`
- source_profile_deltas_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v7-v1/profile_deltas.csv`
- profiles_total: `2500`
- fail_profiles_official: `121`
- pass_profiles_official: `2379`
- fail_rate_official: `0.048400`
- dominant_failing_gate: `g18`

## Transition Counts (raw -> official-v6)

- `pass->pass`: `1750`
- `fail->pass`: `629`
- `fail->fail`: `121`

## Dataset Sensitivity (official fail counts)

- `DS-002`: `31/700`
- `DS-003`: `45/700`
- `DS-004`: `9/200`
- `DS-006`: `27/700`
- `DS-008`: `9/200`

## Top 3 Hypothesized Mechanisms (diagnostic only)

- Remaining failures are dominated by `g18` under official-v6 mapping.
- Gate-coupled signatures indicate hard-regime estimator fragility, not broad lane collapse.
- Zero `pass->fail` transitions indicate policy uplift without degradation side-effects.

## Notes

- Tooling only; no thresholds/formulas changed.
