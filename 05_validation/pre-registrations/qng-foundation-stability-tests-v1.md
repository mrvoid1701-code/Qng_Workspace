# QNG Foundation Stability Tests V1 - Pre-registration

- Date: 2026-03-06
- Status: LOCKED
- Policy ID: `qng-foundation-stability-tests-v1`

## Purpose

Validate EL-consistency of the frozen stability update for `Sigma, chi, phi`
without changing equations or thresholds post-run.

## Fixed Runner

```text
python scripts/run_qng_el_consistency_v1.py
```

## Locked Blocks

`--block-specs` fixed to:

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

## Locked EL-Consistency Gates

Per profile (`all_pass`):

1. `sigma_abs_median <= 0.020`
2. `sigma_abs_p90 <= 0.030`
3. `sigma_abs_max <= 0.060`
4. `global_abs_p90 <= 0.030`
5. `global_abs_max <= 0.060`
6. `chi_abs_max <= 1e-10`
7. `phi_abs_max <= 1e-10`

Dataset/all blocks pass only if all profiles pass.

## Required Artifacts

Output folder:

```text
05_validation/evidence/artifacts/qng-foundation-stability-v1/
```

Required files:

- `profile_residuals.csv`
- `summary.csv`
- `report.md`
- `manifest.json`
- `run-log.txt`

## References

- `03_math/derivations/qng-foundation-stability-v1.md`
- `03_math/derivations/qng-stability-action-v1.md`
- `03_math/derivations/qng-stability-update-v1.md`

## Anti Post-Hoc Policy

1. No threshold edits after results.
2. No equation edits in EL-check lane after results.
3. Any change requires:
   - new prereg version (`...-v2.md`)
   - new artifact folder/version
   - explicit v1 vs v2 comparison.
