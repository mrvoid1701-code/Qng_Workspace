# GR Stage-3 G11/G12 Candidate-v2 Pre-Registration

Date: 2026-03-02  
Protocol ID: `gr-stage3-g11-g12-candidate-v2`

## Intent

Address Stage-3 primary fail signatures (`G11`, `G12`, and `G11+G12`) with candidate-only estimators, without changing official gate formulas/thresholds.

Official policy remains unchanged until prereg closure.

## Input Evidence Anchor

- Stage-3 primary summary: `05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv`
- Stage-3 failure taxonomy: `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/`

Observed fail signatures on primary:

- `G11`: `15`
- `G12`: `11`
- `G11+G12`: `4`

## Candidate Definitions (No Threshold Tuning)

### G11a-v2 (candidate, robust high-signal rank)

Use candidate decision only when legacy `G11` fails.

1. Keep direct pass if `G11` already passes in baseline.
2. Else require baseline structural subgates: `G11b=pass`, `G11c=pass`, `G11d=pass`.
3. Source/target remain physics-aligned with current stack:
   - `S(i)=|L_rw sigma_norm(i)|`
   - `T(i)=|R_smooth(i)|`
4. High-signal subset: top 20% by `S`.
5. Correlation checks:
   - `|Spearman_hs| >= 0.20` OR
   - `|Spearman_hs_trimmed| >= 0.20` (trim 10% tails by `|T|`)
6. Multi-peak aware branch (taxonomy-guided):
   - detect `multi_peak` via existing diagnostic (`peak2/peak1 >= 0.98`, `dist_norm <= 0.10`)
   - if `multi_peak=true`, prefer trimmed rank criterion (same `0.20` threshold).

All numeric thresholds above are inherited/frozen from prior G11 candidate stack (`0.20`, quantile 0.80, trim 0.10).

### G12d-v2 (candidate, robust radial-slope)

Use candidate decision only when legacy `G12` fails with `G12d` failure while `G12a/b/c` remain pass.

1. Keep direct pass if `G12` already passes in baseline.
2. Else compute robust slope on radial profile from existing `gr_solutions.csv` bins.
3. Binning stability guard:
   - reuse existing bins; add diagnostics for low-support bins (`min_bin_count`, `nonempty_bins`)
   - apply trimmed robust fit over supported bins (diagnostic-only preprocessing).
4. Decision threshold remains unchanged:
   - candidate `G12d-v2` pass only if robust slope `< -0.03`.

No new acceptance thresholds are introduced beyond baseline slope threshold.

## Evaluation Blocks

### Primary (frozen)

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`

### Attack A (seed shift)

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3601..4100`

### Attack B (holdout datasets)

- datasets: `DS-004,DS-008`
- seeds: `3401..3600`

## Promotion Criteria (Hard)

For each block (primary, attack A, attack B):

1. `degraded_vs_v1 = 0` (mandatory).
2. Per-dataset non-degradation (mandatory).

Global:

1. `improved_vs_v1 > 0` on primary.
2. `improved_vs_v1 >= 0` on attacks.
3. Publish side-by-side `v1` vs candidate-v2 tables for `G11`, `G12`, and `Stage3`.

If any degraded profile appears, candidate-v2 is not promoted.

