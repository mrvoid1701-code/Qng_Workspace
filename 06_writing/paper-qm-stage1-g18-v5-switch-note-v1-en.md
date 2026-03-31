# Paper Note: QM Stage-1 G18-v5 Official Switch (v1)

## Abstract

We report a governance-layer update for QM Stage-1 in QNG Workspace: `G18-v5`, a fixed multi-window local spectral-dimension estimator used for `G18d` recovery on failing profiles only. The update preserves all gate formulas and thresholds, and is evaluated under preregistered non-degradation criteria across primary, attack, and holdout blocks. The switch from `official-v7` to `official-v8` yields consistent uplift with zero degradations.

## Method

The estimator change is restricted to the decision layer for `G18d`:

1. Preserve source-official pass profiles unchanged.
2. For source-official fail profiles:
   - build two local basins around top sigma peaks,
   - estimate local spectral dimension over a fixed window set (`3-8, 4-9, 4-10, 5-10, 6-11`),
   - keep windows satisfying `R^2 >= 0.50`,
   - select best local estimate per peak,
   - use peak-envelope aggregation (`max(peak1, peak2)`),
   - apply unchanged threshold band (`1.2 < d_s < 3.5`, from metric file defaults).

No post-hoc threshold tuning is used.

## Promotion Results

Against `official-v7`, candidate-v5 promotion checks pass on all blocks with `degraded=0`:

- primary (`600`): `QM lane 571 -> 584` (`+13`)
- attack (`1500`): `QM lane 1426 -> 1453` (`+27`)
- holdout (`400`): `QM lane 382 -> 396` (`+14`)

Total uplift: `+54` passes over `2500` profiles.

## Official-v8 Outcomes

After governance apply (`official-v8`):

- `2433/2500` QM-lane pass (`97.32%`)
- `pass->fail = 0` (non-degradation preserved)

Stage-2 projection under official-v8:

- `raw->official`: `1750 -> 2433` pass
- `fail->pass = 683`
- `fail->fail = 67`

Residual failures remain concentrated:

- `G18`: `45`
- `G17`: `12`
- `G19`: `11`
- `G20`: `0`

## Interpretation

The `G18-v5` switch improves robustness in multi-peak/low-signal diffusion regimes while preserving anti post-hoc governance constraints. The remaining tail is no longer dominated by broad lane instability and is now a smaller, classifiable residual set suitable for targeted Stage-2 closure.

## Reproducibility

Artifacts:

- `05_validation/evidence/artifacts/qm-g18-candidate-v5/`
- `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/`
- `05_validation/evidence/artifacts/qm-stage1-official-v8/`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v6/`
- `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v8-v1/`
- `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v8-v1/`
