# RESULT: QM Stage-1 G18-v7 + G19-v2 Official Switch (V1)

Date: 2026-03-05  
Duration (this sprint): ~25 minutes

## What Was Done

- Added `G19-v2` candidate + evaluator:
  - `scripts/tools/run_qm_g19_candidate_eval_v2.py`
  - `scripts/tools/evaluate_qm_g19_promotion_v1.py`
- Ran `G19-v2` primary/attack/holdout promotion checks
- Ran `G18-v7` (parameterized over v6 runner) on top of `G19-v2` outputs
- Applied official switch `v10 -> v11`
- Refreshed baseline + regression guard (`v9`)
- Refreshed Stage-2 raw-vs-official projection (`v11`)

## Key Results

Official Stage-1 (v11):

- Primary: `597/600`
- Attack: `1492/1500`
- Holdout: `400/400`
- Total: `2489/2500` PASS (`+19` vs v10)

Residual fail profile count:

- `11/2500`

Residual gate mix:

- `G17`: `7` (`G17b`)
- `G19`: `3`
- `G18`: `1` (`G18b`)
- `G20`: `0`

Stage-2 projection under official-v11:

- `1750/2500 -> 2489/2500`
- improved `fail->pass`: `739`
- degraded `pass->fail`: `0`

## Evidence Paths

- G19 candidate: `05_validation/evidence/artifacts/qm-g19-candidate-v2/`
- G19 promotion eval: `05_validation/evidence/artifacts/qm-g19-v2-promotion-eval-v1/`
- G18 candidate v7: `05_validation/evidence/artifacts/qm-g18-candidate-v7/`
- G18 promotion eval v7: `05_validation/evidence/artifacts/qm-g18-v7-promotion-eval-v1/`
- Official v11: `05_validation/evidence/artifacts/qm-stage1-official-v11/`
- Baseline/guard v9: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v9/`
- Stage-2 comparison v11: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v11-v1/`
- Stage-2 taxonomy v11: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v11-v1/`
