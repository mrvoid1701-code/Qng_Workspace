# RESULT: GR Stage-3 Fail Closure v1

Date: 2026-03-04  
Scope: diagnostic-only closure package for remaining GR Stage-3 fails (`597/600` -> investigate final `3/600`)

## What Was Executed

1. Strict fail taxonomy on official Stage-3 summary:
- source: `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv`
- runner: `scripts/tools/analyze_stage3_failures_v1.py`
- output root: `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/`

2. Nearest-pass neighbor extraction (same dataset, nearest seeds) for each fail profile:
- output: `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/nearest_pass_neighbors.csv`

## Main Readout

Official status remains:
- `Stage-3 official v3 = 597/600 pass`
- remaining fail count: `3` profiles (`0.5%`)

Fail pattern:
- `G11` only: `3/3`
- `G12/G7/G8/G9`: no fails inside remaining strict fail scope

Cause classes (strict fail taxonomy):
- `g11b_slope_instability`: `1`
- `weak_corr_multi_peak`: `1`
- `weak_corr_sparse_graph`: `1`

Dataset sensitivity:
- `DS-002`: 1 fail
- `DS-003`: 1 fail
- `DS-006`: 1 fail

## Fail Profiles (exact)

1. `DS-002 seed 3436`  
- class: `g11b_slope_instability`
- signature: `g11a=fail`, `g11b=fail`

2. `DS-003 seed 3491`  
- class: `weak_corr_sparse_graph`
- signature: `g11a=fail`, `g11b=pass`, sparse-graph regime flag

3. `DS-006 seed 3436`  
- class: `weak_corr_multi_peak`
- signature: `g11a=fail`, `g11b=pass`, multi-peak regime flag

Nearest-pass comparisons show local sensitivity:
- each fail has immediate pass neighbors at `|delta_seed|=1` in same dataset.

## Anti Post-Hoc Status

- No threshold changes.
- No physics formula changes.
- This package is diagnostics + governance preparation only.

## Recommendation

Proceed with a single candidate lane (`G11-v5`, candidate-only), preregistered:
- same blocks: primary (`3401..3600`), attack (`3601..4100`), holdout (`DS-004/008`)
- promotion rule: improvement on remaining fail signatures + `degraded=0` everywhere
- official switch only after prereg pass.

## Files

- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/fail_profiles.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/class_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/dataset_fail_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/nearest_pass_neighbors.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/report.md`

