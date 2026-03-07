# D4 Stage-2 Winner V12 Strict (Prereg)

## Scope

- Lane: `d4-stage2-winner-v12-strict`
- Goal: reduce v11 collateral regressions while preserving v11 gain on seed 3403.
- Formula remains frozen: `WINNER_V1_M8C`.

## Single Allowed Change (v12)

Keep v10/v11 point-level focus weights unchanged, but replace v11 aggregation:

- v11 aggregation: median over per-galaxy weighted objective
- v12 aggregation: trimmed mean over per-galaxy weighted objective

Point-level weight (unchanged):

`w_i = 1 + focus_gamma * (r_i / (r_i + r_tail_kpc)) * 1/sqrt(1 + g_bar_i/a0)`

Per-galaxy weighted objective:

`J_g = sum_{i in g} w_i * ((v_obs_i - v_pred_i)/sigma_i)^2 / sum_{i in g} w_i`

Train objective for parameter fit (single v12 change):

`J_train = trimmed_mean_g(J_g, trim_frac=0.10)`

All strict evaluation metrics remain unchanged (standard unweighted chi2/N and same thresholds).

## Locked Formula (unchanged)

`v_pred^2 = bt + r * k * sqrt(g_bar * g_dag) * exp(-g_bar / g_dag)`

with:
- `g_bar = bt / r`
- fitted params per split: `k >= 0`, `g_dag > 0`

## Locked Data + Splits

- dataset_id: `DS-006`
- dataset_csv_rel: `data/rotation/rotation_ds006_rotmod.csv`
- dataset_sha256: `1067802fb376629095ab4a0f8d8358eadd0dda488f046305659ac966d1ab556c`
- split_seeds: `3401,3402,3403,3404,3405`
- train_frac: `0.70`

## Locked Constants + Search

- focus_gamma: `2.0`
- r_tail_kpc: `4.0`
- galaxy_trim_frac: `0.10`
- fit bounds unchanged:
- `k in [0.05, 8.0]`
- `g_dag/a0 in [0.1, 5.0]`
- `g_dag` coarse grid: 60 points + local refinement (40 points)

Compatibility lock fields kept unchanged for evaluator:
- tau_grid: `0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50`
- alpha_grid: `0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3`

## Locked Evaluation Criteria (unchanged)

- `min_holdout_improve_vs_null_pct = 10`
- `max_holdout_mond_worse_pct = 0`
- `max_generalization_gap_pp = 20`
- `max_holdout_delta_aic_dual_minus_mond = 0`
- `max_holdout_delta_bic_dual_minus_mond = 0`

## Promotion Objective

Primary objective for v12:
- keep/improve v11 gain on seed `3403`
- remove v11 collateral degradations (notably seeds `3401` and `3404`)
- with unchanged strict thresholds and governance locks.
