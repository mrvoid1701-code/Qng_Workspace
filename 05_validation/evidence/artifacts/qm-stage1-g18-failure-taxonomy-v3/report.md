# G18 Failure Taxonomy (v1)

- generated_utc: `2026-03-05T08:24:35.288529Z`
- profiles_total: `2500`
- g18_fail_profiles: `45`
- g18_pass_profiles: `2455`
- g18_fail_rate: `0.018000`

## Dominant G18 Failing Subgates

- `g18d_status`: `45` fail occurrences
- `g18b_status`: `1` fail occurrences

## Dataset Sensitivity

- `DS-003`: `20/700` fail (`0.028571`)
- `DS-002`: `15/700` fail (`0.021429`)
- `DS-004`: `2/200` fail (`0.010000`)
- `DS-008`: `2/200` fail (`0.010000`)
- `DS-006`: `6/700` fail (`0.008571`)

## Regime Patterns (Fail Cases)

- `signal_regime`:
  - `unknown`: `45` fails (within-fail `1.000000`)
- `density_regime`:
  - `sparse`: `24` fails (within-fail `0.533333`)
  - `mid_density`: `15` fails (within-fail `0.333333`)
  - `dense`: `6` fails (within-fail `0.133333`)
- `peak_regime`:
  - `multi_peak`: `45` fails (within-fail `1.000000`)
  - `single_peak`: `0` fails (within-fail `0.000000`)
- `geometry_regime`:
  - `normal_geometry`: `41` fails (within-fail `0.911111`)
  - `degenerate_geometry`: `4` fails (within-fail `0.088889`)

## Top 3 Fail Signatures

- `G18D`: `44`
- `G18B+G18D`: `1`

## Top 3 Hypothesized Mechanisms (No Changes Applied)

- Subgate-dominant mechanism: `g18d_status` dominates G18 failures, indicating concentration around one information-geometry observable.
- Dataset sensitivity mechanism: `DS-003` has the highest G18 fail-rate, suggesting topology/regime dependence in the QM info lane.
- Feature-linked mechanism: `g18d_value` has strongest correlation with G18 fail (`r=-0.236897`), indicating failures cluster in specific signal/geometry regimes.

## Output Files

- `g18_fail_cases.csv`
- `g18_pass_cases.csv`
- `pattern_summary_g18_subgates.csv`
- `regime_summary.csv`
- `feature_correlations.csv`
