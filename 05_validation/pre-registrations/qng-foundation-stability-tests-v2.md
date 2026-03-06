# QNG Foundation Stability Tests V2 - Pre-registration

- Date: 2026-03-06
- Status: LOCKED
- Policy ID: `qng-foundation-stability-tests-v2`

## Purpose

Validate EL-consistency for frozen stability dynamics (`Sigma, chi, phi`) using
an independent one-step comparator and non-diluted global residual metric.

## Fixed Runner

```text
python scripts/run_qng_el_consistency_v1.py
```

## Locked Blocks

`--block-specs`:

```text
STABILITY-PRIMARY:3401-3403:36:60;
STABILITY-ATTACK:4401-4403:36:60;
STABILITY-HOLDOUT:3501-3502:42:80
```

## Locked Grids

- `edge_prob in {0.08, 0.18, 0.32}`
- `chi_scale in {0.50, 1.00, 1.50}`
- `noise_level in {0.00, 0.01, 0.03}`
- `phi_shock in {0.00, 0.40}`

## Locked Comparison Rule

Per step, compute:

- `U_current`: output of `scripts/tools/run_stability_stress_v1.py::one_step`
- `U_EL`: output of independent EL predictor in checker script

with identical step inputs and identical RNG state.

Residual per node:

```text
R_sigma = |Sigma_current - Sigma_EL|
R_chi   = |chi_current - chi_EL|
R_phi   = |angle_diff(phi_current, phi_EL)|
R_joint = max(R_sigma, R_chi, R_phi)
```

## Locked Gates

Per profile (`all_pass`):

1. `sigma_abs_median <= 0.020`
2. `sigma_abs_p90 <= 0.030`
3. `sigma_abs_max <= 0.060`
4. `global_abs_p90 <= 0.030` where `global` is from `R_joint`
5. `global_abs_max <= 0.060` where `global` is from `R_joint`
6. `chi_abs_max <= 1e-10`
7. `phi_abs_max <= 1e-10`

Dataset/block pass only if all profiles pass.

## Required Artifacts

Output folder:

```text
05_validation/evidence/artifacts/qng-foundation-stability-v2/
```

Required files:

- `profile_residuals.csv`
- `summary.csv`
- `report.md`
- `manifest.json`
- `run-log.txt`

## Anti Post-Hoc Policy

1. No threshold/formula changes after result.
2. Exploratory nonstrict runs must use a separate folder:
   `qng-foundation-stability-v2-nonstrict`.
3. Any methodology/threshold update requires `...-v3.md` and fresh artifacts.
