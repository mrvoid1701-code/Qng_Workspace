# GR Stage-2 Failure Taxonomy (v1)

- generated_utc: `2026-03-02T01:08:38.018737Z`
- source_summary: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv`
- profiles: `600`

## Overview

- `G11` fail: `19/600`
- `G12` fail: `15/600`

## Signature Patterns

### G11

- `G11a`: `18`
- `G11a+G11b`: `1`

### G12

- `G12d`: `15`

## Margin Diagnostics

| metric | n | mean_abs_margin | median_abs_margin |
| --- | --- | --- | --- |
| G11a fail margin | 19 | 0.008479 | 0.007873 |
| G12d fail margin | 15 | 0.074265 | 0.045229 |

## Candidate v2 Prereg Direction (no v1 change)

1. Keep v1 gates unchanged as official Stage-2 baseline.
2. Add candidate-only estimators:
   - `G11a-v2-candidate`: robustness to weak linearity regimes (rank/robust trend diagnostic).
   - `G12d-v2-candidate`: robust radial-decay slope diagnostic (trimmed/bin-stable slope).
3. Evaluate candidate-only on fixed grid (`DS-002/003/006`, seeds `3401..3600`) plus holdout seed block before any promotion.
4. Promotion rule should use non-degradation vs v1 + minimum uplift, pre-registered before reruns.

