# GR Stage-2 Official Switch (G11a-v3 + G12d-v2 frozen)

Superseded on 2026-03-02 by `G11a-v4` governance update:

- `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`

Date: 2026-03-02  
Effective tag: `gr-stage2-g11-v3-official`

## Why This Switch Exists

`G11a-v3` was evaluated as candidate-only with frozen prereg criteria and passed on:

1. primary grid (`DS-002/003/006`, seeds `3401..3600`),
2. attack A (`DS-002/003/006`, seeds `3601..4100`),
3. holdout attack B (`DS-004/008`, seeds `3401..3600`).

Decision source:

- `05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/promotion_decision.md`

## Frozen Official Policy (v3)

1. `G11` official now uses `G11a-v3` fallback:
   - keep `G11` pass if it already passes under official-v2, OR
   - for v2-fail rows, require `G11b/G11c/G11d` pass and Poisson-source high-signal rule:
     - source proxy `S(i)=|L_rw sigma_norm(i)|`
     - target proxy `T(i)=|R_smooth(i)|`
     - high-signal subset = top 20% by `S`
     - `|Spearman(S,T)| >= 0.20`
     - `|Pearson(S,T)| >= 0.20`
2. `G12` remains frozen at official-v2 status (`G12d-v2` unchanged).

No formula or threshold edits were made in gate runner scripts.

## Promotion Criteria (Pre-registered)

Primary:

- `degraded_vs_v2 = 0`
- `improved_vs_v2 >= 5`
- per-dataset non-degradation
- `weak_corr_drop >= 2`

Attack A / B:

- `degraded_vs_v2 = 0`
- `improved_vs_v2 >= 1`
- weak-corr drop non-negative (`>=1` for A, `>=0` for B in prereg config)

## Governance Application Results

Applied on frozen official-v2 summary (`n=600`):

- `G11`: `587/600 -> 594/600`
- `G12`: `600/600` (unchanged)
- `STAGE2`: `587/600 -> 594/600`
- `improved_vs_v2 = 7`
- `degraded_vs_v2 = 0`

Evidence package:

- `05_validation/evidence/artifacts/gr-stage2-official-v3/`

## Implementation

Official policy application runner:

- `scripts/tools/run_gr_stage2_official_v3.py`

This runner computes official Stage-2 status from frozen summaries and writes:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`

## Historical Record

Previous Stage-2 governance switch (`G11a-v2 + G12d-v2`) remains documented in:

- `docs/GR_STAGE2_OFFICIAL_SWITCH.md`
