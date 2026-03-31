# G15b Multi-Peak Diagnosis (v1)

## Definition

- `multi_peak = (peak_2/peak_1 >= 0.98) AND (distance_norm >= 0.10)`

## Overall

- Runs: `600`
- Multi-peak runs: `106`
- Non-multi-peak runs: `494`
- `v1` fail rate (multi-peak): `0.283`
- `v1` fail rate (non-multi-peak): `0.095`
- `v1` fail-rate lift (multi - non): `0.188`
- `v2` fail rate (multi-peak): `0.000`
- `v2` fail rate (non-multi-peak): `0.000`

## Per Dataset

### DS-002
- Runs: `200` (multi-peak: `28`)
- `v1` fail multi/non: `0.036` / `0.000`
- `v2` fail multi/non: `0.000` / `0.000`

### DS-003
- Runs: `200` (multi-peak: `53`)
- `v1` fail multi/non: `0.547` / `0.320`
- `v2` fail multi/non: `0.000` / `0.000`

### DS-006
- Runs: `200` (multi-peak: `25`)
- `v1` fail multi/non: `0.000` / `0.000`
- `v2` fail multi/non: `0.000` / `0.000`

## Artifacts

- `05_validation\evidence\artifacts\g15b-multipeak-diagnosis-v1\multipeak_diagnosis.csv`
- `05_validation\evidence\artifacts\g15b-multipeak-diagnosis-v1\multipeak_summary.json`
