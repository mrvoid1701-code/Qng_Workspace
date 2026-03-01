# G15b Multi-Peak Sensitivity Sweep

## Sweep Grid

- ratio thresholds: `0.95, 0.97, 0.98, 0.99`
- distance thresholds: `0.05, 0.10, 0.15`
- combinations tested: `12`

## Robustness Summary (ALL datasets combined)

- Cases with positive v1 fail-rate lift (multi - non): `12/12`
- Cases with zero v2 fail in both groups: `12/12`

Interpretation:

- If `v1_fail_lift_multi_minus_non` stays positive across the grid, the fragility trend is not tied to one arbitrary threshold pair.
- If `v2` stays at zero fail in both groups, stability claim for `v2` is threshold-robust under this diagnostic family.

## Artifacts

- `C:\Users\tigan\Desktop\qng workspace\Qng_Workspace\05_validation\evidence\artifacts\g15b-multipeak-diagnosis-v1\multipeak_sensitivity.csv`
