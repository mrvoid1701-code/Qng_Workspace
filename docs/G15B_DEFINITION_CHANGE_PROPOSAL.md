# G15b Definition Change Proposal

## Status

- `G15b-v2` is promoted as the **official decision gate** for G15b.
- `G15b-v1` remains a **legacy diagnostic / sanity check** (single-peak-friendly proxy).
- Thresholds and formulas are unchanged.

## Why this proposal exists

- `G15b-v1` assumes a **single dominant peak + radial shells** around that peak.
- This assumption can break on **multi-peak datasets** (notably `DS-003`), where radial shells around one peak are not a stable proxy for potential depth classes.
- `G15b-v2` uses **potential quantiles** (`top 10% U` vs `bottom 10% U`), invariant to peak multiplicity and directly tied to the field used by the metric.

## Physical Interpretation

- `G15b-v1` is a **geometric proxy**: radial shells around one selected center.
- `G15b-v2` is a **potential-aligned proxy**: it compares Shapiro-delay response across quantiles of `U`, the field that defines the weak-field metric response.
- Framing consequence:
  - `v1` can be useful as a single-peak sanity check.
  - `v2` is the decision gate because it tracks the physically relevant ordering variable (`U`) and is invariant to peak multiplicity.

## Definitions

- `G15b-v1` (legacy):
  `shapiro_ratio_v1 = mean(delta_S | r <= r_33_from_primary_peak) / mean(delta_S | r >= r_66_from_primary_peak)`
- `G15b-v2` (official):
  `inner = top 10% U`, `outer = bottom 10% U`
  `shapiro_ratio_v2 = mean(delta_S | inner) / mean(delta_S | outer)`
- Threshold for both: `> 2.0` (unchanged).

## Pre-Registered Promotion Rule (anti post-hoc)

`G15b-v2` becomes official only if all of the following are true:

- `N = 3` datasets: `DS-002`, `DS-003`, `DS-006`
- `M = 200` fixed seeds per dataset: `3401..3600`
- Same formulas and same threshold (`> 2.0`) with no tuning between registration and run
- Required outcome: `G15b-v2` passes all `N x M = 600` runs

## Criterion-Met Evidence (2026-03-01)

Sources:

- `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/summary_v1_vs_v2_200seeds_per_dataset.csv`
- `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/stats_v1_vs_v2_200seeds_per_dataset.json`

Observed:

- `G15b-v2`: `600/600` pass
- `G15b-v1`: `523/600` pass
- `DS-003` specifically:
  `G15b-v1 = 124/200`, `G15b-v2 = 200/200`

## Targeted Fragility Diagnosis

To explain *why* `v1` fails (not only that it fails), we run a multi-peak diagnostic:

- multi-peak proxy:
  `multi_peak = (peak_2/peak_1 >= 0.98) AND (distance_norm >= 0.10)`
- source:
  `05_validation/evidence/artifacts/g15b-multipeak-diagnosis-v1/multipeak_summary.json`

Key result:

- Overall `v1` fail rate rises from `0.095` (non-multi-peak) to `0.283` (multi-peak), lift `+0.188`
- On `DS-003`, `v1` fail rises from `0.320` to `0.547` under the same proxy
- `v2` remains stable (`0.000` fail in both groups)

Sensitivity robustness check (threshold family):

- ratio thresholds: `0.95, 0.97, 0.98, 0.99`
- distance thresholds: `0.05, 0.10, 0.15`
- artifact target:
  `05_validation/evidence/artifacts/g15b-multipeak-diagnosis-v1/multipeak_sensitivity.csv`
- expected decision criterion:
  positive `v1` fail-rate lift across the grid while `v2` remains stable.
- observed (ALL datasets, 12 combinations):
  - positive `v1` lift: `12/12`
  - `v1` lift range: `+0.107423` to `+0.384483`
  - non-zero `v2` fail cases: `0/12`

## Reporting Convention

Keep both metrics visible in reports:

- `G15b-v1`: radial-shell Shapiro proxy (legacy diagnostic)
- `G15b-v2`: potential-quantile Shapiro proxy (official decision gate)
