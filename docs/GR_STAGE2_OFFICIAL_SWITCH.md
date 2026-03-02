# GR Stage-2 Official Switch (G11a-v2 + G12d-v2)

Date: 2026-03-02  
Effective tag: `gr-stage2-g11g12-v2-official`

## Why This Switch Exists

Stage-2 candidate v1 showed:

- `G12d-v2`: strong uplift with zero degradation
- `G11a-v2` (initial): zero uplift

Stage-2 candidate v2 fixed the `G11a` decision layer using a frozen high-signal correlation rule while keeping gate formulas and thresholds unchanged.

## Frozen Official Policy

Official Stage-2 mapping is now:

1. `G11` uses `G11a-v2` decision layer:
   - keep `G11a-v1` pass directly, OR
   - require `G11b/G11c/G11d` pass and high-signal:
     - `|Spearman(rho,R)| >= 0.20`
     - `|Pearson(rho,R)| >= 0.20`
2. `G12` uses `G12d-v2` decision layer:
   - keep `G12d-v1` pass directly, OR
   - robust slope pass (`slope < -0.03`, unchanged threshold)

No threshold/formula edits were made in:

- `scripts/run_qng_einstein_eq_v1.py`
- `scripts/run_qng_gr_solutions_v1.py`

Switch is governance-layer decision mapping over frozen run artifacts.

## Promotion Criteria (Frozen Before Switch)

To prevent moving-goalposts:

1. Primary grid threshold: `Stage-2 pass rate >= 97.5%`
2. `degraded_vs_v1 = 0`
3. `improved_vs_v1 > 0`
4. Per-dataset non-degradation
5. Same checks pass on attack A + holdout attack B

## Decision Evidence

Primary (`DS-002/003/006`, seeds `3401..3600`):

- `G11`: `581/600 -> 587/600` (improved `6`, degraded `0`)
- `G12`: `585/600 -> 600/600` (improved `15`, degraded `0`)
- `STAGE2`: `570/600 -> 587/600` (`97.833%`, improved `17`, degraded `0`)

Attack A (`DS-002/003/006`, seeds `3601..4100`):

- `G11`: `1426/1500 -> 1451/1500` (improved `25`, degraded `0`)
- `G12`: `1392/1500 -> 1495/1500` (improved `103`, degraded `0`)
- `STAGE2`: `1346/1500 -> 1447/1500` (improved `101`, degraded `0`)

Attack B (`DS-004/008`, seeds `3401..3600`):

- `G11`: `390/400 -> 394/400` (improved `4`, degraded `0`)
- `G12`: `388/400 -> 400/400` (improved `12`, degraded `0`)
- `STAGE2`: `380/400 -> 394/400` (improved `14`, degraded `0`)

Source:

- `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/promotion_decision.md`

## Implementation

Official policy application runner:

- `scripts/tools/run_gr_stage2_official_v2.py`

This runner computes official Stage-2 status from frozen Stage-2 profile runs and writes:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`

Execution artifact (600-profile rerun on frozen Stage-2 grid):

- `05_validation/evidence/artifacts/gr-stage2-official-v2/`
