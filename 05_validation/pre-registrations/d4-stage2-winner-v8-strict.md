# D4 Stage-2 Winner V8 Strict (Prereg)

## Scope

- Lane: `d4-stage2-winner-v8-strict`
- Goal: verify that the already-winning rotation formula from D7/D9b remains stable under strict Stage-2 governance.
- Formula ID: `WINNER_V1_M8C`

## Locked Formula

`v_pred^2 = bt + r * k * sqrt(g_bar * g_dag) * exp(-g_bar / g_dag)`

where:
- `g_bar = bt / r`
- fitted params per split: `k >= 0`, `g_dag > 0`
- units:
- `v` in `km/s`
- `r` in `kpc`
- `bt` in `km^2/s^2`
- `g_bar`, `g_dag` in `km^2/s^2/kpc`

## Locked Data + Splits

- dataset_id: `DS-006`
- dataset_csv_rel: `data/rotation/rotation_ds006_rotmod.csv`
- dataset_sha256: `1067802fb376629095ab4a0f8d8358eadd0dda488f046305659ac966d1ab556c`
- split_seeds: `3401,3402,3403,3404,3405`
- train_frac: `0.70`

## Locked Governance Metadata

- test_id: `d4-stage2-winner-v8-strict`
- candidate_list: `winner_v1_m8c` (single candidate)
- baseline_mond: `MOND_RAR_train_fit_per_split`
- grid_selection_objective: `winner_v1_direct_fit`

Compatibility lock fields kept for evaluator consistency:
- tau_grid: `0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50`
- alpha_grid: `0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3`

WINNER internal fit metadata (fixed by implementation):
- g_dag search over `[0.1*a0, 5.0*a0]`, 60 points + local refinement
- k search in `[0.05, 8.0]` (1D golden search)

## Locked Evaluation Criteria (unchanged)

Use existing strict evaluator thresholds:
- `min_holdout_improve_vs_null_pct = 10`
- `max_holdout_mond_worse_pct = 0`
- `max_generalization_gap_pp = 20`
- `max_holdout_delta_aic_dual_minus_mond = 0`
- `max_holdout_delta_bic_dual_minus_mond = 0`

## A/B Equivalence Requirement

Run equivalence check between D4-v8 outputs and direct D9 WINNER_V1 implementation on the same split seeds.
Acceptance: max absolute delta <= `1e-4` for:
- train chi2/N
- holdout chi2/N
- fitted `k`
- fitted `g_dag`
