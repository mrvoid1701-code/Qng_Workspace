# QM Stage-1 G17b Failure Taxonomy (v1)

- generated_utc: `2026-03-04T10:06:20.514694+00:00`
- profiles_total: `2500`
- g17b_fail_profiles: `115`
- g17b_pass_profiles: `2385`
- g17b_fail_rate: `0.046000`

## Dataset Sensitivity

- `DS-002`: `0/700` fail (`0.000000`)
- `DS-003`: `0/700` fail (`0.000000`)
- `DS-004`: `0/200` fail (`0.000000`)
- `DS-006`: `115/700` fail (`0.164286`)
- `DS-008`: `0/200` fail (`0.000000`)

## Dominant G17b Fail Classes

- `isolated_near_threshold`: `107`
- `coupled_g18_multipeak`: `5`
- `coupled_g19`: `2`

## Top 3 Hypothesized Mechanisms (No Gate Changes Applied)

- Coupled regime mechanism: coupled co-fails are a minority (`7/115`), indicating G17b fragility is mostly isolated.
- Near-threshold mechanism: isolated near-threshold cases dominate (`107/115`), indicating slope-estimator sensitivity near the fixed boundary.
- strongest feature correlation: `g17b_propagator_slope` (`r=0.356442`)

## Inputs

- official summary csvs:
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv`

## Outputs

- `g17b_fail_cases.csv`
- `g17b_pass_cases.csv`
- `pattern_summary.csv`
- `feature_correlations.csv`
