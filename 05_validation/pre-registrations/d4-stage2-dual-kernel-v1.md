# Pre-Registration - D4 Stage-2 Dual-Kernel (v1)

- Date: 2026-03-06
- Test ID: `d4-stage2-dual-kernel-v1`
- Scope: non-circular dual-kernel rotation test on DS-006 real data

## Fixed Command

```powershell
python scripts/run_d4_stage2_dual_kernel_v1.py `
  --dataset-id DS-006 `
  --dataset-csv data/rotation/rotation_ds006_rotmod.csv `
  --seed 3401 `
  --train-frac 0.70 `
  --s1-lambda 0.28 `
  --s2-const 0.355 `
  --r0-kpc 1.0 `
  --tau-grid 0.5,1,2,3,5,8,12,20,30,50 `
  --alpha-grid 0.3,0.5,0.7,1.0,1.3 `
  --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1 `
  --write-artifacts `
  --no-plots
```

## Locked Model Definition

- `v_pred^2 = baryon_term + k1 * H1_tau + k2 * H2_alpha`
- `H1_tau`: exponential memory kernel over S1-weighted baryonic source
- `H2_alpha`: long-range power-law kernel over S2-weighted baryonic source
- Kernels use only `radius` and `baryon_term` (no `v_obs` in kernel construction)
- Fit coefficients are constrained to `k1 >= 0`, `k2 >= 0`

## Locked Evaluation Criteria

Use:

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_v1.py `
  --summary-json 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/d4_stage2_dual_kernel_summary.json `
  --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v1/evaluation-v1 `
  --min-holdout-improve-vs-null-pct 10 `
  --max-holdout-mond-worse-pct 20 `
  --max-generalization-gap-pp 25
```

Decision rule:

- `PASS` only if all evaluator checks pass.
- Otherwise `HOLD`.

## Stop Conditions

- No post-hoc edits to:
  - split seed/fraction
  - tau/alpha grids
  - constants `s1_lambda`, `s2_const`, `r0_kpc`
  - evaluator thresholds above
- Any change requires a new prereg file (`d4-stage2-dual-kernel-v2.md`).
