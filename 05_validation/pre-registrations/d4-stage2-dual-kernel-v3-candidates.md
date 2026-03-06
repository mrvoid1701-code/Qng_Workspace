# Pre-Registration - D4 Stage-2 Candidate Formulas (v3)

- Date: 2026-03-06
- Test ID: `d4-stage2-dual-kernel-v3-candidates`
- Purpose: controlled candidate lane after strict-v2 forensics
- Policy: anti post-hoc (`prereg -> run -> evaluate`, no threshold edits)

## Fixed Data / Splits / Constants

1. dataset:
   - `data/rotation/rotation_ds006_rotmod.csv`
2. split seeds:
   - `3401,3402,3403,3404,3405`
3. train fraction:
   - `0.70`
4. fixed constants:
   - `s1_lambda = 0.28`
   - `s2_const = 0.355`
   - `r0_kpc = 1.0`
   - `r_tail_kpc = 4.0`
5. fixed grids:
   - `tau_grid = 0.5,1,2,3,5,8,12,20,30,50`
   - `alpha_grid = 0.3,0.5,0.7,1.0,1.3`

## Candidate Formulas (only these two)

Baseline features (same as v2):

- `H1_tau`
- `H2_alpha`

Candidate C1 (`outer_tail`):

```text
v_pred^2 = bt + k1*H1 + k2*H2 + k3*H2*(r/(r+r_tail))
```

Candidate C2 (`cross_bridge`):

```text
v_pred^2 = bt + k1*H1 + k2*H2 + k3*sqrt(max(H1*H2,0))
```

Constraints:

- `k1 >= 0`, `k2 >= 0`, `k3 >= 0`
- no other candidate formulas allowed in this lane

## Fixed Commands

Run:

```powershell
python scripts/run_d4_stage2_dual_kernel_candidates_v3.py `
  --test-id d4-stage2-dual-kernel-v3-candidates `
  --dataset-id DS-006 `
  --dataset-csv data/rotation/rotation_ds006_rotmod.csv `
  --split-seeds 3401,3402,3403,3404,3405 `
  --train-frac 0.70 `
  --s1-lambda 0.28 `
  --s2-const 0.355 `
  --r0-kpc 1.0 `
  --r-tail-kpc 4.0 `
  --tau-grid 0.5,1,2,3,5,8,12,20,30,50 `
  --alpha-grid 0.3,0.5,0.7,1.0,1.3 `
  --candidates outer_tail,cross_bridge `
  --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v3-candidates `
  --write-artifacts `
  --no-plots
```

Evaluate:

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_candidates_v3.py `
  --per-seed-csv 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v3-candidates/per_seed_candidate_summary.csv `
  --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v3-candidates/evaluation-v1 `
  --min-holdout-improve-vs-null-pct 10 `
  --max-holdout-mond-worse-pct 0 `
  --max-generalization-gap-pp 20 `
  --max-holdout-delta-aic-dual-minus-mond 0 `
  --max-holdout-delta-bic-dual-minus-mond 0
```

## Promotion Rule (Strict)

For a candidate to be `PASS`:

1. each split seed must pass all strict checks,
2. candidate decision is `PASS` only if pass count is `N/N` seeds.

Global decision:

- `PASS` if at least one candidate is `PASS`,
- else `HOLD`.

## Lock Rule

No edits allowed after observing results to:

1. split seeds,
2. constants,
3. tau/alpha grids,
4. candidate formulas,
5. evaluator thresholds.

Any change requires `...-v4...` prereg.
