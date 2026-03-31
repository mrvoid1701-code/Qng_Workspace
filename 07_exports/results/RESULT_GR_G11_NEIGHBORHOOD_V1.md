# RESULT: GR G11 Neighborhood Quickcheck v1

Date: 2026-03-04  
Window: ~1 hour sprint deliverable  
Scope: local-seed neighborhood analysis around remaining GR Stage-3 fails (`597/600` official)

## What Ran

- Script: `scripts/tools/analyze_gr_stage3_g11_fail_neighborhood_v1.py`
- Input: `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv`
- Output folder: `05_validation/evidence/artifacts/gr-stage3-g11-neighborhood-v1/`
- Seed neighborhood: `+/-5` around each fail anchor (same dataset)

## Main Results

All three remaining fails are **isolated** in local neighborhoods:

- `DS-002 seed 3436`: `1/11` fail in window (isolated), `g11a_fail=1`, `g11b_fail=1`
- `DS-003 seed 3491`: `1/11` fail in window (isolated), `g11a_fail=1`, `g11b_fail=0`
- `DS-006 seed 3436`: `1/11` fail in window (isolated), `g11a_fail=1`, `g11b_fail=0`

Interpretation:

- this does **not** look like broad local instability;
- it looks like narrow edge-case sensitivity at specific seed/regime signatures.

## Anti Post-Hoc Status

- No threshold changes.
- No formula changes.
- Diagnostic-only analysis from already generated official summaries.

## Files

- `05_validation/evidence/artifacts/gr-stage3-g11-neighborhood-v1/fail_seed_neighborhood.csv`
- `05_validation/evidence/artifacts/gr-stage3-g11-neighborhood-v1/neighborhood_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-g11-neighborhood-v1/report.md`

## Next Action (ready)

- Launch candidate `G11-v5` prereg lane focused on the 3 isolated signatures, with strict `degraded=0` on primary/attack/holdout before any official switch.
