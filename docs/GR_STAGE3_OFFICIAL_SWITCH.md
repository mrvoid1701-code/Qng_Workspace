# GR Stage-3 Official Switch (G11/G12 v2 policy)

Superseded on 2026-03-02 by `G11/G12 v3` governance update:

- `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md`

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

## Governance Application Results

Primary 600-profile rerun (`DS-002/003/006`, `3401..3600`):

- prereg rerun package: `05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1/`
  - `stage3_pass=570/600`
- official-v2 rerun package: `05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/`
  - `G11`: `581/600 -> 593/600`
  - `G12`: `585/600 -> 599/600`
  - `Stage-3`: `570/600 -> 592/600`
  - `improved_vs_v1=22`
  - `degraded_vs_v1=0`

## Baseline Guard Refresh

Refreshed Stage-3 official baseline:

- baseline: `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json`
- latest guard: `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json`
- decision: `PASS` (`profiles_mismatch=0`, `profiles_missing=0`)

## Remaining Known Limitation Classes (official-v2 primary)

Strict fail taxonomy over remaining `8` primary fails:

- fail taxonomy package:
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/`
- pattern split:
  - `G11`: `7`
  - `G12`: `1`
- dominant cause classes:
  - `weak_corr_multi_peak`: `3`
  - `weak_corr_sparse_graph`: `2`
  - `g11b_slope_instability`: `1`
  - `weak_corr_low_signal`: `1`
  - `slope_instability`: `1`
