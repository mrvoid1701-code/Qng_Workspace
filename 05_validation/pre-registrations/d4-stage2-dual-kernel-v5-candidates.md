# Pre-Registration - D4 Stage-2 Candidate Formulas (v5)

- Date: 2026-03-06
- Test ID: `d4-stage2-dual-kernel-v5-candidates`
- Purpose: v5 follow-up after v4 findings (boundary + parameter collapse)
- Policy: anti post-hoc (`prereg -> run -> evaluate`)

## Why v5

1. retain direct `chi2` in velocity space (`v`) for coefficient estimation.
2. push grid lower for boundary-hit diagnostics (`tau`, `alpha`).
3. reduce redundancy with minimal candidate set (single dominant component / focused two-term model).
4. apply low-accel + outer emphasis only in fit objective (evaluation remains strict unchanged).

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

## Locked Grids

- `tau_grid = 0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50`
- `alpha_grid = 0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3`

## Locked Candidate Set (exactly two)

1. `outer_lowaccel_single`:

```text
v_pred^2 = bt + k1*H2*(r/(r+r_tail))/sqrt(1 + g_bar/a0)
```

2. `outer_lowaccel_focus`:

```text
v_pred^2 = bt + k1*H1 + k2*H2*(r/(r+r_tail))/sqrt(1 + g_bar/a0)
```

with:

```text
g_bar = bt/r
a0 = A0_INTERNAL (fixed constant)
```

Fit objective lock:

```text
chi2_focus = sum_i w_i * ((v_obs_i - v_pred_i)/v_err_i)^2
w_i = 1 + gamma * (r_i/(r_i+r_tail)) * 1/sqrt(1 + g_bar_i/a0)
gamma = 2.0 (locked)
grid selection objective = argmin_{tau,alpha} chi2_focus(train)
```

Constraints:

- all coefficients are nonnegative.

## Fixed Commands

Run:

```powershell
python scripts/run_d4_stage2_dual_kernel_candidates_v5.py `
  --test-id d4-stage2-dual-kernel-v5-candidates `
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
  --candidates outer_lowaccel_single,outer_lowaccel_focus `
  --focus-gamma 2.0 `
  --outdir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v5-candidates `
  --write-artifacts `
  --no-plots
```

Evaluate:

```powershell
python scripts/tools/evaluate_d4_stage2_dual_kernel_candidates_v5.py `
  --per-seed-csv 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v5-candidates/per_seed_candidate_summary.csv `
  --manifest-json 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v5-candidates/manifest.json `
  --out-dir 05_validation/evidence/artifacts/d4-stage2-dual-kernel-v5-candidates/evaluation-v1 `
  --min-holdout-improve-vs-null-pct 10 `
  --max-holdout-mond-worse-pct 0 `
  --max-generalization-gap-pp 20 `
  --max-holdout-delta-aic-dual-minus-mond 0 `
  --max-holdout-delta-bic-dual-minus-mond 0
```

## Promotion Rule

Candidate `PASS` only if all split seeds pass strict checks (`N/N`) and seed coverage is complete.
Global `PASS` only if at least one candidate is `PASS` and governance lock checks are all `PASS`.

## Lock Rule

No edits after seeing results to:

1. split seeds,
2. constants,
3. grids,
4. candidate formulas,
5. dataset lock (`dataset_csv_rel`, `dataset_sha256`),
6. evaluator lock metadata checks,
7. evaluator thresholds.
