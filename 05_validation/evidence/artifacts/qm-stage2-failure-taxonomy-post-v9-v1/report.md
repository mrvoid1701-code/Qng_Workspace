# QM Stage-2 Failure Taxonomy Post-v6 (v1)

- generated_utc: `2026-03-05T08:31:29.052484+00:00`
- source_profile_deltas_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v9-v1/profile_deltas.csv`
- profiles_total: `2500`
- fail_profiles_official: `35`
- pass_profiles_official: `2465`
- fail_rate_official: `0.014000`
- dominant_failing_gate: `g18`

## Transition Counts (raw -> official-v6)

- `pass->pass`: `1750`
- `fail->pass`: `715`
- `fail->fail`: `35`

## Dataset Sensitivity (official fail counts)

- `DS-002`: `5/700`
- `DS-003`: `10/700`
- `DS-004`: `0/200`
- `DS-006`: `20/700`
- `DS-008`: `0/200`

## Top 3 Hypothesized Mechanisms (diagnostic only)

- Remaining failures are dominated by `g18` under official-v6 mapping.
- Gate-coupled signatures indicate hard-regime estimator fragility, not broad lane collapse.
- Zero `pass->fail` transitions indicate policy uplift without degradation side-effects.

## Notes

- Tooling only; no thresholds/formulas changed.
