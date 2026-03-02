# GR Stage-3 Official Switch (G11/G12 v2 policy)

Date: 2026-03-02  
Effective tag: `gr-stage3-g11g12-v2-official`

## Why This Switch Exists

Stage-3 candidate-v2 (`G11/G12`) passed prereg closure on:

1. primary (`DS-002/003/006`, seeds `3401..3600`),
2. attack A (`DS-002/003/006`, seeds `3601..4100`),
3. attack B holdout (`DS-004/008`, seeds `3401..3600`).

Decision evidence:

- `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/report.md`

## Frozen Official Policy (v2)

Official Stage-3 mapping is now:

1. `G11` official uses candidate-v2 decision status.
2. `G12` official uses candidate-v2 decision status.
3. `G7/G8/G9` statuses remain inherited from frozen source runs.
4. Stage-3 decision remains lane-complete:
   - `lane_3p1` + `lane_strong_field` + `lane_tensor` + `lane_geometry` + `lane_conservation`.

No gate formulas or thresholds were changed.

## Promotion Criteria (Pre-registered)

For primary + both attack blocks:

- `degraded_vs_v1 = 0` (mandatory),
- per-dataset non-degradation (mandatory),
- primary net uplift required (`improved_vs_v1 > 0`).

All criteria were satisfied before this governance switch.

## Implementation

Official policy application runner:

- `scripts/tools/run_gr_stage3_official_v2.py`

This runner computes official Stage-3 status from frozen candidate-v2 summaries and writes:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`
