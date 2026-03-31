# RESULT: QM Stage-1 G19-v4 Official Switch (V1)

Date: 2026-03-05  
Duration (this sprint): ~45 minutes

## What Was Done

- Added candidate evaluator:
  - `scripts/tools/run_qm_g19_candidate_eval_v4.py`
- Added hybrid `G19d` candidate logic:
  - high-signal median slope path (carry-over)
  - local-window best-slope fallback for multi-peak regimes
- Executed candidate runs and promotion evals for:
  - primary (`600`)
  - attack (`1500`)
  - holdout (`400`)
- Applied official switch `v13 -> v14`
- Refreshed baseline + regression guard (`v12`)
- Refreshed Stage-2 projection + taxonomy under official-v14

## Key Results

Official Stage-1 (v14):

- Primary: `600/600`
- Attack: `1500/1500`
- Holdout: `400/400`
- Total: `2500/2500` PASS (`+3` vs v13)

Residual fail profile count:

- `0/2500`

Residual gate mix:

- `G19`: `0`
- `G18`: `0`
- `G17`: `0`
- `G20`: `0`

Stage-2 projection under official-v14:

- `1750/2500 -> 2500/2500`
- improved `fail->pass`: `750`
- degraded `pass->fail`: `0`

## Evidence Paths

- G19 candidate v4: `05_validation/evidence/artifacts/qm-g19-candidate-v4/`
- G19 promotion eval v4: `05_validation/evidence/artifacts/qm-g19-v4-promotion-eval-v1/`
- Official v14: `05_validation/evidence/artifacts/qm-stage1-official-v14/`
- Baseline/guard v12: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v12/`
- Stage-2 comparison v14: `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v14-v1/`
- Stage-2 taxonomy v14: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v14-v1/`

## Scope Guard

- no threshold changes
- no formula changes
- governance-layer candidate-to-official only
