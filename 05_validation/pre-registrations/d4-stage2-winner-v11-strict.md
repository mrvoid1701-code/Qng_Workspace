# D4 Stage-2 Winner V11 Strict (Prereg)

## Scope

- Lane: `d4-stage2-winner-v11-strict`
- Goal: improve train->holdout stability on strict seeds with one conceptual change only.
- Formula remains frozen: `WINNER_V1_M8C`.

## Single Allowed Change (v11)

Keep the same point-level focus weights as v10, but switch train fit aggregation to robust per-galaxy objective.

Point-level weight (unchanged):

`w_i = 1 + focus_gamma * (r_i / (r_i + r_tail_kpc)) * 1/sqrt(1 + g_bar_i/a0)`

Per-galaxy weighted objective:

`J_g = sum_{i in g} w_i * ((v_obs_i - v_pred_i)/sigma_i)^2 / sum_{i in g} w_i`

Train objective for parameter fit (single v11 change):

`J_train = median_g (J_g)`

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

Primary objective for v11:
- reduce `generalization_gap_pp` on seed `3403` under threshold `<= 20`
- while keeping no degradation on the other strict checks across all five seeds.
