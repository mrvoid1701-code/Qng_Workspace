# Pre-Registration - D4 Stage-2 v7 Strict

- Date: 2026-03-07
- Test ID: `d4-stage2-dual-kernel-v7-strict`
- Purpose: strict evaluation of one fixed v7 setup chosen from v7-exp
- Policy: anti post-hoc (`prereg -> run -> evaluate`)

## Fixed Selection Input

- source aggregate csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-v7-exp-v1/aggregate_lambda_summary.csv`
- selected lambda_s: `0.000000`
- selected lambda_e: `0.100000`

## Locked Data / Splits / Constants

- dataset_id: `DS-006`
- dataset_csv: `data/rotation/rotation_ds006_rotmod.csv`
- split_seeds: `3401,3402,3403,3404,3405`
- train_frac: `0.7`
- s1_lambda: `0.28`
- s2_const: `0.355`
- r0_kpc: `1.0`
- r_tail_kpc: `4.0`
- focus_gamma: `2.0`

## Locked Grids

- tau_grid: `0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50`
- alpha_grid: `0.02,0.05,0.1,0.2,0.3,0.5,0.7,1,1.3`

## Locked Formula

```text
v_pred^2 = bt + k1*H1 + k2*Outer
Outer = H2*(r/(r+r_tail))/sqrt(1 + g_bar/a0), g_bar=bt/r, k1,k2>=0
selection objective = argmin_{tau,alpha} [chi2_focus + lambda_s*R_smooth + lambda_e*R_edge]
```

## Strict Criteria

- same evaluator thresholds as current strict MOND lane (unchanged)

## Lock Rule

No edits after seeing strict results to:
1. selected lambdas
2. dataset/splits/constants
3. tau/alpha grids
4. evaluator thresholds
