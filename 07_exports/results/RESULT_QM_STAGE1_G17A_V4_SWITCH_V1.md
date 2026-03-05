# RESULT: QM Stage-1 G17a-v4 Official Switch (V1)

Date: 2026-03-05  
Duration (this sprint): ~10 minutes

## What Was Done

- Added `G17a-v4` candidate evaluator:
  - `scripts/tools/run_qm_g17a_candidate_eval_v4.py`
- Ran candidate + promotion eval on:
  - primary (`DS-002/003/006`, `3401..3600`)
  - attack (`DS-002/003/006`, `3601..4100`)
  - holdout (`DS-004/008`, `3401..3600`)
- Applied official switch `v9 -> v10`
- Refreshed baseline + regression guard (`v8`)
- Refreshed Stage-2 raw-vs-official projection (`v10`)

## Key Results

Official Stage-1 (v10):

- Primary: `591/600`
- Attack: `1479/1500`
- Holdout: `400/400`
- Total: `2470/2500` PASS (`+5` vs v9)

Residual fail profile count:

- `30/2500`

Dominant residual gates:

- `G18`: `12`
- `G19`: `11`
- `G17`: `7` (subgate-dominant `G17b`)
- `G20`: `0`

Stage-2 projection under official-v10:

- `1750/2500 -> 2470/2500`
- improved `fail->pass`: `720`
- degraded `pass->fail`: `0`

## Evidence Paths

- Candidate v4: `05_validation/evidence/artifacts/qm-g17a-candidate-v4/`
- Promotion eval v4: `05_validation/evidence/artifacts/qm-g17a-v4-promotion-eval-v1/`
- Official v10: `05_validation/evidence/artifacts/qm-stage1-official-v10/`
- Baseline/guard v8: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v8/`
- Stage-2 comparison v10: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v10-v1/`
- Stage-2 taxonomy v10: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v10-v1/`
