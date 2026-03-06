# Pre-Registration - D4 Stage-2 Dual-Kernel (v2 strict vs MOND)

- Date: 2026-03-06
- Test ID: `d4-stage2-dual-kernel-v2-strict-vs-mond`
- Scope: strict physical benchmark against MOND on real DS-006 data
- Lane: governance only (`prereg -> run -> evaluate`), no model formula changes

## Fixed Run Command

```powershell
python scripts/run_d4_stage2_dual_kernel_v1.py `
  --test-id d4-stage2-dual-kernel-v2-strict-vs-mond `
  --dataset-id DS-006 `
  --dataset-csv data/rotation/rotation_ds006_rotmod.csv `
  --seed 3401 `
  --train-frac 0.70 `
  --s1-lambda 0.28 `
  --s2-const 0.355 `
  --r0-kpc 1.0 `
  --tau-grid 0.5,1,2,3,5,8,12,20,30,50 `
  --alpha-grid 0.3,0.5,0.7,1.0,1.3 `
  --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond `
  --write-artifacts `
  --no-plots
```

## Locked Model Definition

Same as v1:

- `v_pred^2 = baryon_term + k1 * H1_tau + k2 * H2_alpha`
- kernels depend only on radius + baryon term (no `v_obs` in kernels)
- constrained fit: `k1 >= 0`, `k2 >= 0`
- fixed theory constants and fixed tau/alpha grid above

## Fixed Strict Evaluator

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_v2.py `
  --summary-json 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/d4_stage2_dual_kernel_summary.json `
  --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/evaluation-v2 `
  --min-holdout-improve-vs-null-pct 10 `
  --max-holdout-mond-worse-pct 0 `
  --max-train-mond-worse-pct 5 `
  --max-generalization-gap-pp 20 `
  --max-holdout-delta-aic-dual-minus-mond 0 `
  --max-holdout-delta-bic-dual-minus-mond 0
```

## Decision Rule

`PASS` only if all checks pass:

1. holdout improve vs null >= 10%
2. holdout dual is not worse than MOND (`mond_worse_pct <= 0`)
3. train dual is not far worse than MOND (`<= 5%`)
4. train/holdout generalization gap <= 20 pp
5. holdout `delta AIC (dual-mond) <= 0`
6. holdout `delta BIC (dual-mond) <= 0`

Else decision is `HOLD`.

## Anti Post-Hoc Lock

No edits allowed after seeing results to:

1. split seed or train fraction
2. fixed constants (`s1_lambda`, `s2_const`, `r0_kpc`)
3. tau/alpha search grid
4. evaluator thresholds above

Any change requires a new prereg file (`...-v3...`).
