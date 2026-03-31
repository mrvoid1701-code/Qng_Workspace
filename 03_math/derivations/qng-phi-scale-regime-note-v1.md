# QNG PHI Scale Regime Note v1

## Objective

Check whether changing `PHI_SCALE` from `0.10` to `0.08` is a weak-field regime control choice, not post-hoc tuning.

## Sweep Design

- PHI scale grid: `0.04, 0.06, 0.08, 0.10, 0.12`
- Datasets: `DS-002`, `DS-003`, `DS-006`
- Seed: `3401` (fixed for all runs)
- Gates executed per point: `G10..G16`
- No formulas or thresholds changed.

Artifacts:
- `05_validation/evidence/artifacts/phi_scale_sweep_v1/summary.csv`
- `05_validation/evidence/artifacts/phi_scale_sweep_v1/run-log.txt`

## Interpretation Frame

`PHI_SCALE` multiplies the weak-field potential amplitude (`U ~ |Phi|`), so it is a regime-amplitude control.
In this view, changing `PHI_SCALE` should produce smooth trends in first-order/PPN diagnostics, without requiring threshold edits.

## Sweep Table (from summary.csv)

| Dataset | PHI_SCALE | G10 | G11 | G12 | G13 | G14 | G15 | G16 | ALL | G15a gamma_dev | G15d EP_ratio | G15b shapiro_ratio | G13 E_cov drift | G14 E_cov drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 0.04 | pass | pass | pass | pass | pass | pass | pass | pass | 0.011144 | 0.045558 | 2.385873 | 8.634375e-04 | 2.303446e-04 |
| DS-002 | 0.06 | pass | pass | pass | pass | pass | pass | pass | pass | 0.016827 | 0.066428 | 2.402253 | 0.002064 | 9.274196e-05 |
| DS-002 | 0.08 | pass | pass | pass | pass | pass | pass | pass | pass | 0.022587 | 0.086167 | 2.419454 | 0.002911 | 8.405627e-04 |
| DS-002 | 0.10 | pass | pass | pass | pass | pass | pass | pass | pass | 0.028426 | 0.104868 | 2.437506 | 0.003297 | 0.001104 |
| DS-002 | 0.12 | pass | pass | pass | pass | pass | pass | pass | pass | 0.034344 | 0.122614 | 2.456441 | 0.003314 | 7.953096e-04 |
| DS-003 | 0.04 | pass | pass | pass | pass | pass | fail | pass | fail | 0.012791 | 0.038579 | 1.921528 | 0.001602 | 2.398256e-04 |
| DS-003 | 0.06 | pass | pass | pass | pass | pass | fail | pass | fail | 0.019325 | 0.056188 | 1.932662 | 0.003376 | 0.001018 |
| DS-003 | 0.08 | pass | pass | pass | pass | pass | fail | pass | fail | 0.025954 | 0.072804 | 1.944373 | 0.004385 | 0.001927 |
| DS-003 | 0.10 | pass | pass | pass | pass | pass | fail | pass | fail | 0.032680 | 0.088513 | 1.956680 | 0.004486 | 0.001810 |
| DS-003 | 0.12 | pass | pass | pass | pass | pass | fail | pass | fail | 0.039506 | 0.103386 | 1.969606 | 0.003873 | 8.561168e-04 |
| DS-006 | 0.04 | pass | pass | pass | pass | pass | pass | pass | pass | 0.008744 | 0.053607 | 3.376955 | 7.518060e-04 | 5.145897e-04 |
| DS-006 | 0.06 | pass | pass | pass | pass | pass | pass | pass | pass | 0.013194 | 0.078338 | 3.401573 | 5.847506e-06 | 6.101013e-04 |
| DS-006 | 0.08 | pass | pass | pass | pass | pass | pass | pass | pass | 0.017696 | 0.101833 | 3.427312 | 7.356327e-04 | 7.335762e-04 |
| DS-006 | 0.10 | pass | pass | pass | pass | pass | pass | pass | pass | 0.022253 | 0.124189 | 3.454210 | 0.001318 | 1.494170e-04 |
| DS-006 | 0.12 | pass | pass | pass | pass | pass | pass | pass | pass | 0.026865 | 0.145491 | 3.482312 | 0.001746 | 3.708877e-04 |

Note: in current gate naming, E_cov drift in G13 is gate row `G13b` with metric `E_cov_drift`.

## Results

1. `G15a gamma_dev` is monotonic increasing with PHI scale on all 3 datasets.
2. `G15d EP_ratio` is monotonic increasing with PHI scale on all 3 datasets.
3. `G15b shapiro_ratio` is monotonic increasing with PHI scale on all 3 datasets.
4. `G13 E_cov drift` and `G14 E_cov drift` stay small and below threshold for all points; they are not strictly monotonic on all datasets.
5. Pass robustness by dataset:
   - `DS-002`: `all_pass = 5/5`
   - `DS-003`: `all_pass = 0/5` (only G15 fails; specifically Shapiro ratio `< 2.0` across entire scanned range)
   - `DS-006`: `all_pass = 5/5`

## Conclusion

Within this sweep, behavior is trend-consistent with a weak-field regime control:
- increasing `PHI_SCALE` smoothly increases PPN deviations (`gamma_dev`, `EP_ratio`) and Shapiro contrast;
- no threshold edits were needed, and non-PPN energy-drift checks remain stable.

This does **not** support a post-hoc "single-point rescue" narrative for `0.08`, because:
- `DS-002` and `DS-006` pass across the full scanned range,
- `DS-003` fails G15 across the full scanned range (no PHI value in this grid flips it to pass).

Therefore, `PHI_SCALE = 0.08` is justified as a conservative weak-field operating point (lower PPN deviation vs `0.10`), not as a tuned value that uniquely forces cross-dataset pass.
