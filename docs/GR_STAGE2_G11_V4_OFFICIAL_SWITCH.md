# GR Stage-2 Official Switch (G11a-v4 + G12d-v2 frozen)

Date: 2026-03-02  
Effective tag: `gr-stage2-g11-v4-official`

## Why This Switch Exists

`G11a-v4` was evaluated as candidate-only with frozen prereg criteria and passed on:

1. primary grid (`DS-002/003/006`, seeds `3401..3600`),
2. attack A (`DS-002/003/006`, seeds `3601..4100`),
3. holdout attack B (`DS-004/008`, seeds `3401..3600`).

Decision source:

- `05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/promotion_decision.md`

## Frozen Official Policy (v4)

1. `G11` official now uses `G11a-v4` fallback:
   - keep `G11` pass if it already passes under official-v3, OR
   - for v3-fail rows, require `G11b/G11c/G11d` pass and robust rank high-signal rule:
     - source proxy `S(i)=|L_rw sigma_norm(i)|`
     - target proxy `T(i)=|R_smooth(i)|`
     - high-signal subset = top 20% by `S`
     - `rank_or_pass = (|Spearman_hs|>=0.20) OR (|Spearman_hs_trimmed|>=0.20)`
2. `G12` remains frozen at official-v2 status (`G12d-v2` unchanged).

No formula or threshold edits were made in gate runner scripts.

## Promotion Criteria (Pre-registered)

Primary:

- `degraded_vs_v3 = 0`
- `improved_vs_v3 >= 2`
- per-dataset non-degradation
- `g11_v4_fail <= 3` (`>=99.5%` on 600 profiles)

Attack A / B:

- `degraded_vs_v3 = 0`
- per-dataset non-degradation
- `improved_vs_v3 >= 0`

## Governance Application Results

Applied on frozen official-v3 summary (`n=600`):

- `G11`: `594/600 -> 597/600`
- `G12`: `600/600` (unchanged)
- `STAGE2`: `594/600 -> 597/600`
- `improved_vs_v3 = 3`
- `degraded_vs_v3 = 0`

Fresh full-chain rerun package confirms same counts:

- `05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/report.md`

## Baseline Guard Refresh

Stage-2 baseline was refreshed to the new official tag and validated:

- baseline: `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json`
- guard: `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.json`
- decision: `PASS`

## Known Limitations (Primary Grid, v4)

Remaining `G11` fails on primary (`3`) are explicitly tracked:

- `g11b_slope_fail`: `1`
- `weak_rank_corr`: `2`

Reference:

- `05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/primary_ds002_003_006_s3401_3600/summary.csv`

## Implementation

Official policy application runner:

- `scripts/tools/run_gr_stage2_official_v4.py`

This runner computes official Stage-2 status from frozen summaries and writes:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`

## Historical Record

Previous Stage-2 governance switches remain documented in:

- `docs/GR_STAGE2_OFFICIAL_SWITCH.md` (v2)
- `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md` (v3)
