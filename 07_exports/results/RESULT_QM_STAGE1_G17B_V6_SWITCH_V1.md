# RESULT: QM Stage-1 G17b-v6 Official Switch (V1)

Date: 2026-03-05  
Duration (this sprint): ~45 minutes

## What Was Done

- Added candidate evaluator:
  - `scripts/tools/run_qm_g17b_candidate_eval_v6.py`
- Added Make targets for:
  - `qm_g17b_candidate_v6_*`, `qm_g17b_v6_promotion_*`
  - `qm_stage1_official_v12_apply`
  - `qm_stage1_baseline_build_v10`, `qm_stage1_regression_guard_v10`
  - `qm_stage2_raw_vs_official_v12`, `qm_stage2_taxonomy_post_v12`
- Ran candidate + promotion packages on primary/attack/holdout
- Applied official switch `v11 -> v12`
- Refreshed baseline + regression guard (`v10`)
- Refreshed Stage-2 projection (`raw vs official-v12`)

## Key Results

Official Stage-1 (v12):

- Primary: `600/600`
- Attack: `1496/1500`
- Holdout: `400/400`
- Total: `2496/2500` PASS (`+7` vs v11)

Residual fail profile count:

- `4/2500`

Residual gate mix:

- `G19`: `3`
- `G18`: `1`
- `G17`: `0`
- `G20`: `0`

Stage-2 projection under official-v12:

- `1750/2500 -> 2496/2500`
- improved `fail->pass`: `746`
- degraded `pass->fail`: `0`

## Evidence Paths

- G17b candidate v6: `05_validation/evidence/artifacts/qm-g17b-candidate-v6/`
- G17b promotion eval v6: `05_validation/evidence/artifacts/qm-g17b-v6-promotion-eval-v1/`
- Official v12: `05_validation/evidence/artifacts/qm-stage1-official-v12/`
- Baseline/guard v10: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v10/`
- Stage-2 comparison v12: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v12-v1/`
- Stage-2 taxonomy v12: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v12-v1/`

## Scope Guard

- no threshold changes
- no formula changes
- governance-layer candidate-to-official only
