# REPRODUCIBILITY

Exact commands for reproducible GR-chain reruns (housekeeping only, no math edits).

## 1) Rerun G10..G16 for a fixed dataset + seed

Example values:

- `DATASET=DS-002`
- `SEED=3401`
- output root: `07_exports/repro/gr_chain_ds002_s3401`

```bash
python scripts/run_qng_covariant_metric_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g10
python scripts/run_qng_einstein_eq_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g11
python scripts/run_qng_gr_solutions_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g12
python scripts/run_qng_covariant_wave_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g13
python scripts/run_qng_covariant_cons_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g14
python scripts/run_qng_ppn_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g15
python scripts/run_qng_action_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g16
```

## 2) PHI scale sweep

```bash
python scripts/run_qng_phi_scale_sweep_v1.py --datasets DS-002,DS-003,DS-006 --seeds 3401 --phi-scales 0.04,0.06,0.08,0.10,0.12 --out-dir 05_validation/evidence/artifacts/phi_scale_sweep_v1
```

Main outputs:

- `05_validation/evidence/artifacts/phi_scale_sweep_v1/summary.csv`
- `05_validation/evidence/artifacts/phi_scale_sweep_v1/run-log.txt`

## 3) Compare G15b v1 vs v2

```bash
python scripts/run_qng_ppn_debug_v1.py --datasets DS-002,DS-003,DS-006 --seeds 3401 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/qng-ppn-debug-v1
```

Main output:

- `05_validation/evidence/artifacts/qng-ppn-debug-v1/summary_v1_vs_v2.csv`

DS-003 multi-seed stability check:

```bash
python scripts/run_qng_ppn_debug_v1.py --datasets DS-003 --seeds 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/qng-ppn-debug-v1-ds003-seed-sweep
```

## 4) GR regression guard (G10..G16 freeze check)

Run against frozen baseline (`gr-ppn-g15b-v2-official`, grid20 baseline default):

```bash
python scripts/run_qng_gr_regression_guard_v1.py --out-dir 05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check
```

Or via master runner:

```bash
python scripts/run_all.py --group gr-guard
```

Main outputs:

- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/observed_summary.csv`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/regression_report.json`

## 5) Rebuild baseline json from sweep summary (grid20 helper)

Source files for the current deep baseline are tracked here:

- `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/run-log-grid20.txt`

Rebuild command:

```bash
python scripts/tools/build_gr_baseline_from_sweep.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-json 05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json --baseline-id gr-g10-g16-regression-grid20-v1 --effective-tag gr-ppn-g15b-v2-official --effective-commit ebce36d --effective-date-utc 2026-03-01
```

## 6) GR stability diagnostics from grid20 summary

```bash
python scripts/tools/analyze_gr_stability_v1.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stability-v1 --top-k 10 --tag gr-ppn-g15b-v2-official
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stability-v1/dataset_stats.csv`
- `05_validation/evidence/artifacts/gr-stability-v1/worst_cases.csv`
- `05_validation/evidence/artifacts/gr-stability-v1/report.md`
