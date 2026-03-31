# G18 Failure Taxonomy (v1)

- generated_utc: `2026-03-03T02:35:30.341405Z`
- profiles_total: `2500`
- g18_fail_profiles: `169`
- g18_pass_profiles: `2331`
- g18_fail_rate: `0.067600`

## Dominant G18 Failing Subgates

- `g18d_status`: `169` fail occurrences
- `g18b_status`: `1` fail occurrences

## Dataset Sensitivity

- `DS-003`: `70/700` fail (`0.100000`)
- `DS-004`: `14/200` fail (`0.070000`)
- `DS-008`: `14/200` fail (`0.070000`)
- `DS-002`: `46/700` fail (`0.065714`)
- `DS-006`: `25/700` fail (`0.035714`)

## Regime Patterns (Fail Cases)

- `signal_regime`:
  - `unknown`: `169` fails (within-fail `1.000000`)
- `density_regime`:
  - `sparse`: `76` fails (within-fail `0.449704`)
  - `mid_density`: `59` fails (within-fail `0.349112`)
  - `dense`: `34` fails (within-fail `0.201183`)
- `peak_regime`:
  - `multi_peak`: `169` fails (within-fail `1.000000`)
  - `single_peak`: `0` fails (within-fail `0.000000`)
- `geometry_regime`:
  - `normal_geometry`: `148` fails (within-fail `0.875740`)
  - `degenerate_geometry`: `21` fails (within-fail `0.124260`)

## Top 3 Fail Signatures

- `G18D`: `168`
- `G18B+G18D`: `1`

## Top 3 Hypothesized Mechanisms (No Changes Applied)

- Subgate-dominant mechanism: `g18d_status` dominates G18 failures, indicating concentration around one information-geometry observable.
- Dataset sensitivity mechanism: `DS-003` has the highest G18 fail-rate, suggesting topology/regime dependence in the QM info lane.
- Feature-linked mechanism: `g18d_value` has strongest correlation with G18 fail (`r=-0.472772`), indicating failures cluster in specific signal/geometry regimes.

## Output Files

- `g18_fail_cases.csv`
- `g18_pass_cases.csv`
- `pattern_summary_g18_subgates.csv`
- `regime_summary.csv`
- `feature_correlations.csv`
