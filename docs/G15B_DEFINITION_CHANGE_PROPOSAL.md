# G15b Definition Change Proposal

## Status

- `G15b-v1` remains the **official/legacy gate** (current decision path).
- `G15b-v2` is a **candidate gate** (reported side-by-side, not authoritative yet).

## Why this proposal exists

- `G15b-v1` assumes a **single dominant peak + radial shells** around that peak.
- This assumption can break on **multi-peak datasets** (notably `DS-003`), where radial shells around one peak are not a stable proxy for "near stronger potential" vs "far weaker potential".
- `G15b-v2` uses **potential quantiles** (`top 10% U` vs `bottom 10% U`), which is invariant to peak multiplicity and directly tied to the potential field used by the metric.

## Definitions

- `G15b-v1` (legacy):  
  `shapiro_ratio_v1 = mean(delta_S | r <= r_33_from_primary_peak) / mean(delta_S | r >= r_66_from_primary_peak)`
- `G15b-v2` (candidate):  
  `inner = top 10% U`, `outer = bottom 10% U`  
  `shapiro_ratio_v2 = mean(delta_S | inner) / mean(delta_S | outer)`
- Threshold for both: `> 2.0` (unchanged).

## DS-003 multi-seed diagnosis (phi=0.08)

Source:  
`05_validation/evidence/artifacts/qng-ppn-debug-v1-ds003-seed-sweep/summary_v1_vs_v2.csv`

- Seeds tested: `3401..3410` (10 runs)
- `G15b-v1` pass rate: `3/10` (unstable)
- `G15b-v2` pass rate: `10/10` (stable)
- `v1 ratio` range: `1.786072 .. 2.304436`
- `v2 ratio` range: `4.114306 .. 4.860327`

Interpretation: for the DS-003 class, `v1` behaves like a weak estimator under multi-peak geometry, while `v2` is stable under the same thresholds and formulas.

## Promotion Rule (anti post-hoc)

Promote `G15b-v2` to official **only after a pre-registered validation grid passes**:

- `N = 3` datasets (`DS-002`, `DS-003`, `DS-006`)
- `M = 10` fixed seeds per dataset
- Same formulas and threshold (`> 2.0`), no tuning between registration and run
- Required outcome: `G15b-v2` passes all `N × M = 30` runs

Until this criterion is met, reports must include both:

- `G15b-v1`: radial-shell Shapiro proxy (legacy)
- `G15b-v2`: potential-quantile Shapiro proxy (recommended candidate)
