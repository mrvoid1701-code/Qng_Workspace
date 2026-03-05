# QM Stage-2 Failure Taxonomy (v1)

- generated_utc: `2026-03-05T23:35:56.770171+00:00`
- source_profile_deltas_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v14-v1/profile_deltas.csv`
- profiles_total: `2500`
- fail_profiles_official: `0`
- pass_profiles_official: `2500`
- fail_rate_official: `0.000000`
- dominant_failing_gate: `none`

## Transition Counts (raw -> official-v14)

- `pass->pass`: `1750`
- `fail->pass`: `750`

## Dataset Sensitivity (official fail counts)

- `DS-002`: `0/700`
- `DS-003`: `0/700`
- `DS-004`: `0/200`
- `DS-006`: `0/700`
- `DS-008`: `0/200`

## Top 3 Hypothesized Mechanisms (diagnostic only)

- Remaining failures are dominated by `none` under official-v14 mapping.
- Gate-coupled signatures indicate hard-regime estimator fragility, not broad lane collapse.
- Zero `pass->fail` transitions indicate policy uplift without degradation side-effects.

## Notes

- Tooling only; no thresholds/formulas changed.
