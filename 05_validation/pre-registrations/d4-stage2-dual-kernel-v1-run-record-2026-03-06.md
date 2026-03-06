# D4 Stage-2 Dual-Kernel v1 - Run Record (2026-03-06)

Status: executed against locked prereg `d4-stage2-dual-kernel-v1.md`

## Execution

Run command:

```powershell
python scripts/run_d4_stage2_dual_kernel_v1.py --dataset-id DS-006 --dataset-csv data/rotation/rotation_ds006_rotmod.csv --seed 3401 --train-frac 0.70 --s1-lambda 0.28 --s2-const 0.355 --r0-kpc 1.0 --tau-grid 0.5,1,2,3,5,8,12,20,30,50 --alpha-grid 0.3,0.5,0.7,1.0,1.3 --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1 --write-artifacts --no-plots
```

Eval command:

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_v1.py --summary-json 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/d4_stage2_dual_kernel_summary.json --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/evaluation-v1 --min-holdout-improve-vs-null-pct 10 --max-holdout-mond-worse-pct 20 --max-generalization-gap-pp 25
```

## Key Outputs

- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/d4_stage2_dual_kernel_summary.json`
- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/grid_search_results.csv`
- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/model_comparison.csv`
- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/report.md`
- `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/evaluation-v1/evaluation_report.json`

## Snapshot

- best params (train-selected): `tau=0.5`, `alpha=0.3`, `k1=0.163458892`, `k2=0.0`
- holdout `chi2/N`:
  - `null = 270.776399`
  - `MOND = 46.690217`
  - `dual-kernel = 241.639903`
- holdout improvement vs null: `10.760353%`
- holdout worse vs MOND: `417.538620%`
- train/holdout generalization gap (improve-vs-null): `0.491749 pp`

## Decision

- evaluator decision: `HOLD`
- pass checks:
  - holdout improvement vs null: `PASS`
  - generalization gap: `PASS`
- fail checks:
  - not far worse than MOND: `FAIL`

## Governance Note

No threshold/formula edits were made during this run.  
Any model-definition change (kernel forms, grids, constants, split protocol, evaluator thresholds)
requires a new prereg version.
