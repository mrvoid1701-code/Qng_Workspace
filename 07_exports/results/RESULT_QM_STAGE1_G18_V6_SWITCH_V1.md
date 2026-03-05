# RESULT_QM_STAGE1_G18_V6_SWITCH_V1

Date: 2026-03-05

## What was done

- Added `G18-v6` candidate evaluator:
  - `scripts/tools/run_qm_g18_candidate_eval_v6.py`
  - fixed multi-scale basin (`q in {0.15, 0.22}`) + fixed multi-window local `d_s` recovery
  - source official pass is preserved (non-degrading governance mapping)
- Ran candidate on primary/attack/holdout blocks
- Ran promotion checks with `degraded=0` requirement
- Applied official policy switch `v8 -> v9`
- Built new baseline + guard (`v7`) and re-ran Stage-2 projection/taxonomy

## Key results

Official Stage-1 (v9):

- Primary: `590/600` PASS (`+6` vs v8)
- Attack: `1475/1500` PASS (`+22` vs v8)
- Holdout: `400/400` PASS (`+4` vs v8)
- Total: `2465/2500` PASS (`+32` vs v8)
- Degraded transitions: `0`

Stage-2 projection under official-v9:

- `2465/2500` PASS
- `fail->pass = 715`
- `pass->fail = 0`
- residual fails: `35`

Residual fail signature (Stage-2 projection):

- `G18`: `12`
- `G17`: `12`
- `G19`: `11`
- `G20`: `0`

## Output pointers

- Candidate v6: `05_validation/evidence/artifacts/qm-g18-candidate-v6/`
- Promotion eval v6: `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/`
- Official v9: `05_validation/evidence/artifacts/qm-stage1-official-v9/`
- Baseline/guard v7: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v7/`
- Stage-2 comparison v9: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v9-v1/`
- Stage-2 taxonomy v9: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v9-v1/`
