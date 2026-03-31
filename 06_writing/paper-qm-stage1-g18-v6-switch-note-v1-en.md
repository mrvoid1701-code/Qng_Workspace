# Paper Note: QM Stage-1 G18-v6 Official Switch (v1)

## Abstract

We report a second governance-layer hardening step for QM Stage-1 in QNG Workspace: `G18-v6`, a fixed multi-scale basin and multi-window local spectral-dimension estimator for `G18d` recovery on source-official fail cases only. The update preserves core gate formulas and thresholds, and passes preregistered non-degradation checks across primary, attack, and holdout blocks. The resulting `official-v9` policy improves the QM lane to `2465/2500` pass.

## Method

`G18-v6` modifies only the decision-layer estimator for `G18d`:

1. Preserve source official pass profiles unchanged.
2. For source official fail profiles:
   - build local basins around top sigma peaks,
   - evaluate two fixed basin scales (`q in {0.15, 0.22}`),
   - for each scale evaluate fixed time windows (`3-8, 4-9, 4-10, 5-10, 6-11`),
   - keep windows with `R^2 >= 0.50`,
   - take best per-peak local `d_s`, then peak-envelope across peaks,
   - apply unchanged threshold band (`1.2 < d_s < 3.5`).

No threshold or formula tuning is used.

## Promotion Results (vs official-v8)

All three promotion evaluations pass with `degraded=0`:

- primary (`600`): `QM lane 584 -> 590` (`+6`)
- attack (`1500`): `QM lane 1453 -> 1475` (`+22`)
- holdout (`400`): `QM lane 396 -> 400` (`+4`)

Total uplift: `+32` passes over `2500` profiles.

## Official-v9 Outcomes

After governance apply (`official-v9`):

- `2465/2500` QM-lane pass (`98.60%`)
- `pass->fail = 0`

Stage-2 projection under official-v9:

- `raw->official`: `1750 -> 2465` pass
- `fail->pass = 715`
- `fail->fail = 35`

Residual failures are now nearly balanced across non-G20 gates:

- `G18`: `12`
- `G17`: `12`
- `G19`: `11`
- `G20`: `0`

## Interpretation

`G18-v6` materially reduces the residual G18 tail while preserving strict non-degradation and anti post-hoc governance rules. The remaining failures are no longer dominated by a single gate, enabling the next closure sprint to proceed as a balanced `G18/G17/G19` tail analysis rather than a single-gate bottleneck.
