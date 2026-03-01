# Changelog

## 2026-03-01 - G16 failure taxonomy diagnostics (no math changes)

- Added G16 taxonomy runner:
  - `scripts/tools/run_g16_failure_taxonomy_v1.py`
- Added taxonomy artifacts from grid20 profiles:
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_fail_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_pass_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_failure_taxonomy.md`
- Current result snapshot:
  - all observed G16 fails are `G16b`-driven (Einstein coupling R² sub-gate), with `G16a/G16c/G16d` passing.

## 2026-03-01 - GR baseline semantics split (official vs survey)

- Added explicit pass semantics in sweep/guard outputs:
  - `all_pass_official` (uses `G15b-v2`, excludes legacy-v1 effect)
  - `all_pass_diagnostic` (legacy chain including `G15` final)
- Added baseline modes in baseline builder:
  - `--mode survey` (full grid, including expected diagnostic fails)
  - `--mode official` (filtered pass-only official profiles)
- Added official baseline file:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
- Guard default baseline now points to official baseline:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Updated tracked source summary with explicit official/diagnostic pass columns:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`

## 2026-03-01 - GR stability diagnostics (no math changes)

- Added diagnostics tool for G13/G14 drift stability from sweep summaries:
  - `scripts/tools/analyze_gr_stability_v1.py`
- Added baseline-derived outputs:
  - `05_validation/evidence/artifacts/gr-stability-v1/dataset_stats.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/worst_cases.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/report.md`
- Added reproducibility command for this diagnostics pass:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-01 - GR regression guard deep baseline (grid20)

- Added deep baseline config (DS-002/003/006 x seeds 3401..3420, `PHI_SCALE=0.08`):
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json`
- Added baseline builder helper:
  - `scripts/tools/build_gr_baseline_from_sweep.py`
- `gr_baseline_grid20.json` is now maintained as survey baseline (not pass-only official baseline).
- Added provenance source summary and run-log:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/`

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
