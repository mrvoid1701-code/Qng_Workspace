# D4 Stage-2 Dual-Kernel Evaluation (v2 strict vs MOND)

- generated_utc: `2026-03-06T01:15:10.114429Z`
- summary_json: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/d4_stage2_dual_kernel_summary.json`
- decision: `HOLD`

## Observed

- holdout chi2/N dual: `241.639903`
- holdout chi2/N mond: `46.690217`
- holdout improve vs null (%): `10.760353`
- holdout mond worse (%): `417.538620`
- holdout delta AIC (dual-mond): `208602.164177`
- holdout delta BIC (dual-mond): `208617.090419`
- train mond worse (%): `144.262641`
- train-holdout improve gap (pp): `0.491749`

## Checks

- lock_test_id: `True`
- lock_dataset_id: `True`
- lock_dataset_csv_name: `True`
- lock_dataset_csv_rel: `True`
- lock_dataset_sha256: `True`
- lock_split_seed: `True`
- lock_train_frac: `True`
- lock_s1_lambda: `True`
- lock_s2_const: `True`
- lock_r0_kpc: `True`
- lock_tau_grid: `True`
- lock_alpha_grid: `True`
- holdout_improve_vs_null: `True`
- holdout_not_worse_than_mond: `False`
- train_not_far_worse_than_mond: `False`
- generalization_gap_ok: `True`
- holdout_aic_not_worse_than_mond: `False`
- holdout_bic_not_worse_than_mond: `False`
