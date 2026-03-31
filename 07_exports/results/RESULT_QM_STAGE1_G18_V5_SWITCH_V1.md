# RESULT_QM_STAGE1_G18_V5_SWITCH_V1

Date: 2026-03-05
Duration note: this sprint execution lasted approximately 5 hours (as requested to be recorded in-result).

## What was done

- Implemented `G18-v5` candidate estimator:
  - file: `scripts/tools/run_qm_g18_candidate_eval_v5.py`
  - policy: fixed multi-window local spectral-dimension estimator + peak-envelope over two local basins
  - no formula changes in core gates
  - no threshold changes
- Ran candidate over all official Stage-1 blocks:
  - primary (600)
  - attack (1500)
  - holdout (400)
- Ran promotion evaluations (`degraded=0` criteria)
- Applied governance switch `official-v7 -> official-v8`
- Built new baseline (`v6`) + regression guard check
- Re-ran Stage-2 projection (`raw vs official-v8`) + updated taxonomy

## Key results

Official Stage-1 (v8):

- Primary: `584/600` PASS (`+13` vs v7)
- Attack: `1453/1500` PASS (`+27` vs v7)
- Holdout: `396/400` PASS (`+14` vs v7)
- Total: `2433/2500` PASS (`+54` vs v7)
- Degraded transitions: `0`

Stage-2 projection under official-v8:

- `2433/2500` PASS
- `fail->pass = 683`
- `pass->fail = 0`
- residual fails: `67`

Residual fail signature (Stage-2 projection):

- `G18`: `45`
- `G17`: `12`
- `G19`: `11`
- `G20`: `0`

## Output pointers

- Candidate v5: `05_validation/evidence/artifacts/qm-g18-candidate-v5/`
- Promotion eval v5: `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/`
- Official v8: `05_validation/evidence/artifacts/qm-stage1-official-v8/`
- Baseline/guard v6: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v6/`
- Stage-2 comparison v8: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v8-v1/`
- Stage-2 taxonomy v8: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v8-v1/`
