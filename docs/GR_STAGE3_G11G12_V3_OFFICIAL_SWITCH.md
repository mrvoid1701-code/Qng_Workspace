# GR Stage-3 Official Switch (G11/G12 v3 policy)

Date: 2026-03-02  
Effective tag: `gr-stage3-g11g12-v3-official`

## Why This Switch Exists

Stage-3 candidate-v3 closed the fail-closure sprint against official-v2 baseline with:

1. primary uplift and zero degradation,
2. attack uplift and zero degradation,
3. holdout non-degradation.

Decision evidence:

- `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/report.md`
- `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/promotion_decision.md`

## Frozen Official Policy (v3)

Official Stage-3 mapping is now:

1. `G11` official uses candidate-v3 decision status.
2. `G12` official uses candidate-v3 decision status.
3. `G7/G8/G9` statuses remain inherited from frozen source runs.
4. Stage-3 decision remains lane-complete:
   - `lane_3p1` + `lane_strong_field` + `lane_tensor` + `lane_geometry` + `lane_conservation`.

No gate formulas or thresholds were changed.

## Promotion Criteria (Pre-registered)

For primary + both attack blocks:

- `degraded_vs_v2 = 0` (mandatory),
- per-dataset non-degradation (mandatory),
- primary net uplift required (`improved_vs_v2 > 0`).

All criteria were satisfied before this governance switch.

## Governance Application Result (Primary)

Applied on frozen candidate-v3 primary package (`n=600`):

- `G11`: `593/600 -> 597/600`
- `G12`: `599/600 -> 600/600`
- `Stage-3`: `592/600 -> 597/600`
- `improved_vs_v2 = 5`
- `degraded_vs_v2 = 0`

Source package:

- `05_validation/evidence/artifacts/gr-stage3-official-v3/`

## Known Limitations (v3, primary)

Remaining official fails:

- `3/600`, all in `G11`.

Reference packages:

- `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/report.md`

## Implementation

Official policy application runner:

- `scripts/tools/run_gr_stage3_official_v3.py`

This runner computes official Stage-3 status from frozen candidate-v3 summaries and writes:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`
