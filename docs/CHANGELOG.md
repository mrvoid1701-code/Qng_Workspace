# Changelog

## 2026-03-01 - GR/PPN freeze: `gr-ppn-g15b-v2-official`

- Freeze scope: GR/PPN decision policy for G15b.
- Effective gate policy:
  - `G15b-v2` = official decision gate.
  - `G15b-v1` = legacy diagnostic-only gate.
- Promotion baseline commit: `15dd881`.
- Promotion rule source: `docs/G15B_DEFINITION_CHANGE_PROPOSAL.md`.
- Evidence baseline:
  - `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/`
  - `05_validation/evidence/artifacts/g15b-multipeak-diagnosis-v1/`

## 2026-03-01 - GR regression guard baseline (G10..G16)

- Added frozen guard baseline config:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline.json`
- Added automatic checker:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Added reproducibility command documentation:
  - `docs/REPRODUCIBILITY.md`
- Fixed `run_qng_phi_scale_sweep_v1.py` path handling for relative `--out-dir`.
