# G18 Failure Taxonomy (v1)

- generated_utc: `2026-03-03T02:12:29.827930Z`
- profiles_total: `2500`
- g18_fail_profiles: `250`
- g18_pass_profiles: `2250`
- g18_fail_rate: `0.100000`

## Dominant G18 Failing Subgates

- `g18d_status`: `250` fail occurrences
- `g18b_status`: `1` fail occurrences

## Dataset Sensitivity

- `DS-003`: `106/700` fail (`0.151429`)
- `DS-004`: `20/200` fail (`0.100000`)
- `DS-008`: `20/200` fail (`0.100000`)
- `DS-002`: `65/700` fail (`0.092857`)
- `DS-006`: `39/700` fail (`0.055714`)

## Regime Patterns (Fail Cases)

- `signal_regime`:
  - `low_signal`: `143` fails (within-fail `0.572000`)
  - `mid_signal`: `61` fails (within-fail `0.244000`)
  - `high_signal`: `46` fails (within-fail `0.184000`)
- `density_regime`:
  - `sparse`: `116` fails (within-fail `0.464000`)
  - `mid_density`: `82` fails (within-fail `0.328000`)
  - `dense`: `52` fails (within-fail `0.208000`)
- `peak_regime`:
  - `multi_peak`: `250` fails (within-fail `1.000000`)
  - `single_peak`: `0` fails (within-fail `0.000000`)
- `geometry_regime`:
  - `normal_geometry`: `213` fails (within-fail `0.852000`)
  - `degenerate_geometry`: `37` fails (within-fail `0.148000`)

## Top 3 Fail Signatures

- `G18D`: `249`
- `G18B+G18D`: `1`

## Top 3 Hypothesized Mechanisms (No Changes Applied)

- Subgate-dominant mechanism: `g18d_status` dominates G18 failures, indicating concentration around one information-geometry observable.
- Dataset sensitivity mechanism: `DS-003` has the highest G18 fail-rate, suggesting topology/regime dependence in the QM info lane.
- Feature-linked mechanism: `g18d_value` has strongest correlation with G18 fail (`r=-0.581726`), indicating failures cluster in specific signal/geometry regimes.

## Output Files

- `g18_fail_cases.csv`
- `g18_pass_cases.csv`
- `pattern_summary_g18_subgates.csv`
- `regime_summary.csv`
- `feature_correlations.csv`
