# Pre-Registration - D4 Stage-2 Candidate Formula (v6)

- Date: 2026-03-06
- Test ID: `d4-stage2-dual-kernel-v6-candidate`
- Purpose: single reduced-DOF candidate after v6 forensics
- Policy: anti post-hoc (`prereg -> run -> evaluate`)

## Why v6

1. keep strict evaluator thresholds unchanged.
2. reduce redundancy to one amplitude parameter per grid point.
3. keep same locked seeds/dataset/constants as v5.
4. keep model selection objective locked to `chi2_focus(train)`.

## Locked Data / Splits / Constants

1. dataset:
   - `data/rotation/rotation_ds006_rotmod.csv`
2. split seeds:
   - `3401,3402,3403,3404,3405`
3. train fraction:
   - `0.70`
4. constants:
   - `s1_lambda = 0.28`
   - `s2_const = 0.355`
   - `r0_kpc = 1.0`
   - `r_tail_kpc = 4.0`
   - `focus_gamma = 2.0`

## Locked Grids

- `tau_grid = 0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50`
- `alpha_grid = 0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3`
- `mix_grid = 0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0`

## Locked Candidate Set (exactly one)

1. `outer_single_mix_v6`:

```text
outer = H2*(r/(r+r_tail))/sqrt(1 + g_bar/a0)
mix_term = (1-mix)*H1 + mix*outer
v_pred^2 = bt + k*mix_term
```

with:

```text
mix in mix_grid (fixed)
k >= 0
g_bar = bt/r
a0 = A0_INTERNAL (fixed constant)
```

Fit objective lock:

```text
chi2_focus = sum_i w_i * ((v_obs_i - v_pred_i)/v_err_i)^2
w_i = 1 + gamma * (r_i/(r_i+r_tail)) * 1/sqrt(1 + g_bar_i/a0)
gamma = 2.0 (locked)
grid selection objective = argmin_{tau,alpha,mix} chi2_focus(train)
```

## Fixed Commands

Run:

```powershell
python scripts/run_d4_stage2_dual_kernel_candidate_v6.py `
  --test-id d4-stage2-dual-kernel-v6-candidate `
  --dataset-id DS-006 `
  --dataset-csv data/rotation/rotation_ds006_rotmod.csv `
  --split-seeds 3401,3402,3403,3404,3405 `
  --train-frac 0.70 `
  --s1-lambda 0.28 `
  --s2-const 0.355 `
  --r0-kpc 1.0 `
  --r-tail-kpc 4.0 `
  --tau-grid 0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50 `
  --alpha-grid 0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3 `
  --mix-grid 0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 `
  --candidates outer_single_mix_v6 `
  --focus-gamma 2.0 `
  --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v6-candidate `
  --write-artifacts `
  --no-plots
```

Evaluate:

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_candidates_v5.py `
  --per-seed-csv 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v6-candidate/per_seed_candidate_summary.csv `
  --manifest-json 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v6-candidate/manifest.json `
  --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v6-candidate/evaluation-v1 `
  --expected-test-id d4-stage2-dual-kernel-v6-candidate `
  --expected-candidates outer_single_mix_v6 `
  --expected-mix-grid 0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 `
  --min-holdout-improve-vs-null-pct 10 `
  --max-holdout-mond-worse-pct 0 `
  --max-generalization-gap-pp 20 `
  --max-holdout-delta-aic-dual-minus-mond 0 `
  --max-holdout-delta-bic-dual-minus-mond 0
```

## Promotion Rule

- Candidate `PASS` only if all split seeds pass strict checks (`5/5`) with complete coverage.
- Global `PASS` only if governance lock checks are all `PASS`.

## Lock Rule

No edits after seeing results to:

1. split seeds,
2. constants,
3. grids,
4. candidate formula,
5. dataset lock (`dataset_csv_rel`, `dataset_sha256`),
6. evaluator lock metadata checks,
7. evaluator thresholds.
