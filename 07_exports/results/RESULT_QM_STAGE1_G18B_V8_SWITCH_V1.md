# RESULT: QM Stage-1 G18b-v8 Official Switch (V1)

Date: 2026-03-05  
Duration (this sprint): ~35 minutes

## What Was Done

- Added candidate evaluators:
  - `scripts/tools/run_qm_g19_candidate_eval_v3.py` (diagnostic hold, no uplift)
  - `scripts/tools/run_qm_g18b_candidate_eval_v8.py` (official promotion path)
- Added Make targets for:
  - `qm_g19_candidate_v3_*`, `qm_g19_v3_promotion_*`
  - `qm_g18b_candidate_v8_*`, `qm_g18b_v8_promotion_*`
  - `qm_stage1_official_v13_apply`
  - `qm_stage1_baseline_build_v11`, `qm_stage1_regression_guard_v11`
  - `qm_stage2_raw_vs_official_v13`, `qm_stage2_taxonomy_post_v13`
- Applied official switch `v12 -> v13` using `G18b-v8`

## Key Results

Official Stage-1 (v13):

- Primary: `600/600`
- Attack: `1497/1500`
- Holdout: `400/400`
- Total: `2497/2500` PASS (`+1` vs v12)

Residual fail profile count:

- `3/2500`

Residual gate mix:

- `G19`: `3`
- `G18`: `0`
- `G17`: `0`
- `G20`: `0`

Stage-2 projection under official-v13:

- `1750/2500 -> 2497/2500`
- improved `fail->pass`: `747`
- degraded `pass->fail`: `0`

## Evidence Paths

- G19 candidate v3: `05_validation/evidence/artifacts/qm-g19-candidate-v3/`
- G19 promotion eval v3: `05_validation/evidence/artifacts/qm-g19-v3-promotion-eval-v1/`
- G18b candidate v8: `05_validation/evidence/artifacts/qm-g18b-candidate-v8/`
- G18b promotion eval v8: `05_validation/evidence/artifacts/qm-g18b-v8-promotion-eval-v1/`
- Official v13: `05_validation/evidence/artifacts/qm-stage1-official-v13/`
- Baseline/guard v11: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v11/`
- Stage-2 comparison v13: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v13-v1/`
- Stage-2 taxonomy v13: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v13-v1/`

## Scope Guard

- no threshold changes
- no formula changes
- governance-layer candidate-to-official only
