# GR Stage-3 Official-v2 Rerun Decision Note

Date: 2026-03-02

## Inputs

- prereg rerun source: `05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1/summary.csv`
- candidate mapper: `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/rerun_ds002_003_006_s3401_3600/summary.csv`
- official mapping: `05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv`

## Result

- `Stage3 v1 -> official-v2: 570/600 -> 592/600`
- `improved_vs_v1: 22`
- `degraded_vs_v1: 0`

## Guard + Taxonomy

- baseline guard:
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json`
  - decision: `PASS`
- strict fail taxonomy (remaining 8 official fails):
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/report.md`

## Decision

Rerun confirms official-v2 mapping behavior on frozen Stage-3 grid with zero degradation and consistent guard status.
