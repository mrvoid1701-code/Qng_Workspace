# Changelog

## 2026-03-06 - D4 candidate lane v3 (two formulas, multi-split strict prereg)

- Added candidate runner:
  - `scripts/run_d4_stage2_dual_kernel_candidates_v3.py`
- Added strict multi-split evaluator:
  - `scripts/tools/evaluate_d4_stage2_dual_kernel_candidates_v3.py`
- Added prereg:
  - `05_validation/pre-registrations/d4-stage2-dual-kernel-v3-candidates.md`
- Added Make targets:
  - `d4_stage2_candidates_v3_run`
  - `d4_stage2_candidates_v3_eval`
  - `d4_stage2_candidates_v3_pack`
- Updated reproducibility docs:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-06 - D4 forensics v1 (strict-v2 failure segmentation)

- Added analysis script:
  - `scripts/tools/analyze_d4_stage2_forensics_v1.py`
- Added Make target:
  - `d4_stage2_forensics_v1`
- Added reproducibility docs for forensics outputs:
  - `docs/REPRODUCIBILITY.md`
- Forensics outputs (generated from strict-v2 package):
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/forensics-v1/point_residuals.csv`
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/forensics-v1/segment_summary.csv`
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/forensics-v1/worst_galaxies.csv`
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/forensics-v1/report.md`

## 2026-03-06 - Follow-up review fixes (D4 dataset hash lock + v2 strict artifact run)

- Hardened D4 strict evaluator dataset lock:
  - `scripts/tools/evaluate_d4_stage2_dual_kernel_v2.py`
  - added lock checks for:
    - `dataset_csv_rel`
    - `dataset_sha256`
- Hardened D4 runner metadata output:
  - `scripts/run_d4_stage2_dual_kernel_v1.py`
  - summary now includes:
    - `dataset_csv_rel`
    - `dataset_sha256`
- Updated prereg + repro docs:
  - `05_validation/pre-registrations/d4-stage2-dual-kernel-v2-strict-vs-mond.md`
  - `docs/REPRODUCIBILITY.md`
- Executed strict v2 lane run and evaluation package:
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/d4_stage2_dual_kernel_summary.json`
  - `05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/evaluation-v2/evaluation_report.json`
- Observed strict decision on v2 package: `HOLD` (expected under strict-vs-MOND criteria).

## 2026-03-06 - Follow-up hardening from review (EL note correction + D4 v2 lock checks + strict exit)

- Corrected P0-2 formal note wording/proof scope:
  - `03_math/derivations/qng-stability-el-equivalence-v1.md`
  - replaced incorrect implicit-proximal exactness claim with exact explicit Euler / linearized variational surrogate statement
- Hardened D4 strict evaluator governance:
  - `scripts/tools/evaluate_d4_stage2_dual_kernel_v2.py`
  - validates locked metadata (`test_id`, dataset, split seed/fraction, fixed constants, tau/alpha grids)
  - `HOLD` now returns non-zero by default (`--strict-exit`, with optional `--no-strict-exit`)
- Updated prereg/repro docs:
  - `05_validation/pre-registrations/d4-stage2-dual-kernel-v2-strict-vs-mond.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-06 - Stability P0 formal lane (EL equivalence + theorems + convergence rate) + D4 strict-vs-MOND prereg v2

- Added formal derivation notes:
  - `03_math/derivations/qng-stability-el-equivalence-v1.md`
  - `03_math/derivations/qng-stability-theorems-v1.md`
  - `03_math/derivations/qng-discrete-continuum-rate-v1.md`
- Added status tracker:
  - `docs/STABILITY_P0_FORMAL_STATUS_V1.md`
- Added strict D4 prereg vs MOND:
  - `05_validation/pre-registrations/d4-stage2-dual-kernel-v2-strict-vs-mond.md`
- Added strict evaluator tooling:
  - `scripts/tools/evaluate_d4_stage2_dual_kernel_v2.py`
- Updated dual-kernel runner metadata support (no physics changes):
  - `scripts/run_d4_stage2_dual_kernel_v1.py` now accepts `--test-id`
- Added Make targets:
  - `d4_stage2_dual_kernel_v2_run`
  - `d4_stage2_dual_kernel_v2_eval`
  - `d4_stage2_dual_kernel_v2_pack`
- Updated reproducibility doc with v2 strict commands:
  - `docs/REPRODUCIBILITY.md`
- Scope guard:
  - no GR/QM gate threshold changes
  - no physics formula changes

## 2026-03-05 - QM Stage-1 G19-v4 promotion + official-v14 switch + baseline guard v12

- Added candidate evaluator:
  - `scripts/tools/run_qm_g19_candidate_eval_v4.py` (hybrid local-window recovery)
- Added Make targets for:
  - `qm_g19_candidate_v4_*`, `qm_g19_v4_promotion_*`
  - `qm_stage1_official_v14_apply`
  - `qm_stage1_baseline_build_v12`, `qm_stage1_regression_guard_v12`
  - `qm_stage2_raw_vs_official_v14`, `qm_stage2_taxonomy_post_v14`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g19-candidate-v4/`
  - `05_validation/evidence/artifacts/qm-g19-v4-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - G19-v4 lane uplift: primary `+0`, attack `+3`, holdout `+0`
- Applied official QM Stage-1 v14 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v14/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v14/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v14/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v12/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v14`):
  - pass: `2500/2500`
  - improved `fail->pass`: `750`
  - degraded `pass->fail`: `0`
  - residual fail: `0` (`G19=0`, `G18=0`, `G17=0`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G19_V4_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G19V4_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g19-v4-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G18b-v8 promotion + official-v13 switch + baseline guard v11

- Added candidate evaluators:
  - `scripts/tools/run_qm_g19_candidate_eval_v3.py` (diagnostic hold lane)
  - `scripts/tools/run_qm_g18b_candidate_eval_v8.py` (official promotion lane)
- Added Make targets for:
  - `qm_g19_candidate_v3_*`, `qm_g19_v3_promotion_*`
  - `qm_g18b_candidate_v8_*`, `qm_g18b_v8_promotion_*`
  - `qm_stage1_official_v13_apply`
  - `qm_stage1_baseline_build_v11`, `qm_stage1_regression_guard_v11`
  - `qm_stage2_raw_vs_official_v13`, `qm_stage2_taxonomy_post_v13`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g19-candidate-v3/` (no uplift, degraded=0)
  - `05_validation/evidence/artifacts/qm-g19-v3-promotion-eval-v1/` (`HOLD`)
  - `05_validation/evidence/artifacts/qm-g18b-candidate-v8/`
  - `05_validation/evidence/artifacts/qm-g18b-v8-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - G18b-v8 lane uplift: primary `+0`, attack `+1`, holdout `+0`
- Applied official QM Stage-1 v13 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v13/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v13/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v13/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v11/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v13`):
  - pass: `2497/2500`
  - improved `fail->pass`: `747`
  - degraded `pass->fail`: `0`
  - residual fail: `3` (`G19=3`, `G18=0`, `G17=0`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G18B_V8_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G18B_V8_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18b-v8-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G17b-v6 promotion + official-v12 switch + baseline guard v10

- Added candidate evaluator:
  - `scripts/tools/run_qm_g17b_candidate_eval_v6.py`
- Added Make targets for:
  - `qm_g17b_candidate_v6_*`, `qm_g17b_v6_promotion_*`
  - `qm_stage1_official_v12_apply`
  - `qm_stage1_baseline_build_v10`, `qm_stage1_regression_guard_v10`
  - `qm_stage2_raw_vs_official_v12`, `qm_stage2_taxonomy_post_v12`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g17b-candidate-v6/`
  - `05_validation/evidence/artifacts/qm-g17b-v6-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `QM lane 597/600 -> 600/600`
  - attack lane: `QM lane 1492/1500 -> 1496/1500`
  - holdout lane: `QM lane 400/400 -> 400/400`
- Applied official QM Stage-1 v12 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v12/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v12/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v12/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v10/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v12`):
  - pass: `2496/2500`
  - improved `fail->pass`: `746`
  - degraded `pass->fail`: `0`
  - residual fail: `4` (`G19=3`, `G18=1`, `G17=0`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G17B_V6_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G17B_V6_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g17b-v6-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G18-v7 + G19-v2 promotion + official-v11 switch + baseline guard v9

- Added candidate/eval scripts:
  - `scripts/tools/run_qm_g19_candidate_eval_v2.py`
  - `scripts/tools/evaluate_qm_g19_promotion_v1.py`
- Added Make targets for:
  - `qm_g19_candidate_v2_*`, `qm_g19_v2_promotion_*`
  - `qm_g18_candidate_v7_*`, `qm_g18_v7_promotion_*`
  - `qm_stage1_official_v11_apply`
  - `qm_stage1_baseline_build_v9`, `qm_stage1_regression_guard_v9`
  - `qm_stage2_raw_vs_official_v11`, `qm_stage2_taxonomy_post_v11`
- Executed promotion packages:
  - `05_validation/evidence/artifacts/qm-g19-candidate-v2/`
  - `05_validation/evidence/artifacts/qm-g19-v2-promotion-eval-v1/`
  - `05_validation/evidence/artifacts/qm-g18-candidate-v7/`
  - `05_validation/evidence/artifacts/qm-g18-v7-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - G19-v2 lane uplift: primary `+4`, attack `+4`, holdout `+0`
  - G18-v7 lane uplift (post G19-v2): primary `+2`, attack `+9`, holdout `+0`
- Applied official QM Stage-1 v11 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v11/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v11/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v11/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v9/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v11`):
  - pass: `2489/2500`
  - improved `fail->pass`: `739`
  - degraded `pass->fail`: `0`
  - residual fail: `11` (`G17=7`, `G19=3`, `G18=1`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G18_V7_G19_V2_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G18V7_G19V2_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18-v7-g19-v2-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G17a-v4 promotion + official-v10 switch + baseline guard v8

- Added candidate evaluator:
  - `scripts/tools/run_qm_g17a_candidate_eval_v4.py`
- Added Make targets:
  - `qm_g17a_candidate_v4_primary`
  - `qm_g17a_candidate_v4_attack`
  - `qm_g17a_candidate_v4_holdout`
  - `qm_g17a_v4_promotion_primary`
  - `qm_g17a_v4_promotion_attack`
  - `qm_g17a_v4_promotion_holdout`
  - `qm_stage1_official_v10_apply`
  - `qm_stage1_baseline_build_v8`
  - `qm_stage1_regression_guard_v8`
  - `qm_stage2_raw_vs_official_v10`
  - `qm_stage2_taxonomy_post_v10`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g17a-candidate-v4/`
  - `05_validation/evidence/artifacts/qm-g17a-v4-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `QM lane 590/600 -> 591/600`
  - attack lane: `QM lane 1475/1500 -> 1479/1500`
  - holdout lane: `QM lane 400/400 -> 400/400`
- Applied official QM Stage-1 v10 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v10/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v10/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v10/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v8/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v10`):
  - pass: `2470/2500`
  - improved `fail->pass`: `720`
  - degraded `pass->fail`: `0`
  - residual fail: `30` (`G18=12`, `G19=11`, `G17=7`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G17A_V4_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G17A_V4_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g17a-v4-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G18-v6 promotion + official-v9 switch + baseline guard v7

- Added candidate evaluator:
  - `scripts/tools/run_qm_g18_candidate_eval_v6.py`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v6/`
  - `05_validation/evidence/artifacts/qm-g18-v6-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `G18 592/600 -> 598/600`, `QM lane 584/600 -> 590/600`
  - attack lane: `G18 1467/1500 -> 1489/1500`, `QM lane 1453/1500 -> 1475/1500`
  - holdout lane: `G18 396/400 -> 400/400`, `QM lane 396/400 -> 400/400`
- Applied official QM Stage-1 v9 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v9/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v9/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v9/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v7/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v9`):
  - pass: `2465/2500`
  - improved `fail->pass`: `715`
  - degraded `pass->fail`: `0`
  - residual fail: `35` (`G18=12`, `G17=12`, `G19=11`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G18_V6_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G18_V6_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18-v6-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G18-v5 promotion + official-v8 switch + baseline guard v6

- Added candidate evaluator:
  - `scripts/tools/run_qm_g18_candidate_eval_v5.py`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v5/`
  - `05_validation/evidence/artifacts/qm-g18-v5-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `G18 579/600 -> 592/600`, `QM lane 571/600 -> 584/600`
  - attack lane: `G18 1440/1500 -> 1467/1500`, `QM lane 1426/1500 -> 1453/1500`
  - holdout lane: `G18 382/400 -> 396/400`, `QM lane 382/400 -> 396/400`
- Applied official QM Stage-1 v8 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v8/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v8/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v8/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v6/` (`PASS`)
- Stage-2 projection refresh (`raw vs official-v8`):
  - pass: `2433/2500`
  - improved `fail->pass`: `683`
  - degraded `pass->fail`: `0`
  - residual fail: `67` (`G18=45`, `G17=12`, `G19=11`, `G20=0`)
- Added docs/results:
  - `docs/QM_STAGE1_G18_V5_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G18_V5_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18-v5-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-1 G18-v4 promotion + official-v7 switch + baseline guard v5

- Added candidate evaluator:
  - `scripts/tools/run_qm_g18_candidate_eval_v4.py`
- Added Make targets:
  - `qm_g18_candidate_v4_primary`
  - `qm_g18_candidate_v4_attack`
  - `qm_g18_candidate_v4_holdout`
  - `qm_g18_v4_promotion_primary`
  - `qm_g18_v4_promotion_attack`
  - `qm_g18_v4_promotion_holdout`
  - `qm_stage1_official_v7_apply`
  - `qm_stage1_baseline_build_v5`
  - `qm_stage1_regression_guard_v5`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v4/`
  - `05_validation/evidence/artifacts/qm-g18-v4-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `G18 551/600 -> 579/600`, `QM lane 560/600 -> 571/600`
  - attack lane: `G18 1339/1500 -> 1440/1500`, `QM lane 1387/1500 -> 1426/1500`
  - holdout lane: `G18 360/400 -> 382/400`, `QM lane 372/400 -> 382/400`
- Applied official QM Stage-1 v7 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v7/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v7/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v7/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v5/` (`PASS`)
- Added docs/results:
  - `docs/QM_STAGE1_G18_V4_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_BASELINE_GUARD.md` (v5)
  - `07_exports/results/RESULT_QM_STAGE1_G18_V4_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18-v4-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-05 - QM Stage-2 post-v7 comparison + taxonomy refresh

- Added Make targets:
  - `qm_stage2_raw_vs_official_v7`
  - `qm_stage2_taxonomy_post_v7`
- Generated post-v7 evidence packages:
  - `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v7-v1/`
  - `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v7-v1/`
- Key readout (`2500` profiles):
  - raw pass: `1750/2500`
  - official-v7 projected pass: `2379/2500`
  - improved `fail->pass`: `629`
  - degraded `pass->fail`: `0`
- Remaining dominant failing gate (post-v7):
  - `G18` (`99/2500`)
  - `G17` (`12/2500`)
  - `G19` (`11/2500`)
  - `G20` (`0/2500`)
- Added next prereg scaffold:
  - `05_validation/pre-registrations/qm-stage2-g18-candidate-v5.md`
- Scope guard:
  - tooling + diagnostics only
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-2 post-v6 comparison + failure taxonomy

- Added post-v6 taxonomy tool:
  - `scripts/tools/analyze_qm_stage2_post_v6_failures_v1.py`
- Added prereg scaffold for next candidate lane:
  - `05_validation/pre-registrations/qm-stage2-g18-candidate-v4.md`
- Added Make targets:
  - `qm_stage2_raw_vs_official_v6`
  - `qm_stage2_taxonomy_post_v6`
- Generated post-v6 evidence packages:
  - `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v6-v1/`
  - `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-post-v6-v1/`
- Key readout (`2500` profiles):
  - raw pass: `1750/2500`
  - official-v6 projected pass: `2319/2500`
  - improved `fail->pass`: `569`
  - degraded `pass->fail`: `0`
- Remaining dominant failing gate (post-v6):
  - `G18` (`160/2500`)
  - `G17` reduced to `12/2500`
  - `G19` remains low (`11/2500`)
  - `G20` stable (`0/2500` fails)
- Scope guard:
  - tooling + diagnostics only
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-1 G17b-v4 promotion + official-v6 switch + baseline guard v4

- Added candidate evaluator:
  - `scripts/tools/run_qm_g17b_candidate_eval_v4.py`
- Added Make targets:
  - `qm_g17b_candidate_v4_primary`
  - `qm_g17b_candidate_v4_attack`
  - `qm_g17b_candidate_v4_holdout`
  - `qm_g17b_v4_promotion_primary`
  - `qm_g17b_v4_promotion_attack`
  - `qm_g17b_v4_promotion_holdout`
  - `qm_stage1_official_v6_apply`
  - `qm_stage1_baseline_build_v4`
  - `qm_stage1_regression_guard_v4`
- Executed candidate + promotion packages:
  - `05_validation/evidence/artifacts/qm-g17b-candidate-v4/`
  - `05_validation/evidence/artifacts/qm-g17b-v4-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `G17 564/600 -> 596/600`, `QM lane 529/600 -> 560/600`
  - attack lane: `G17 1416/1500 -> 1492/1500`, `QM lane 1316/1500 -> 1387/1500`
  - holdout lane: unchanged non-degrading (`G17 400/400`, `QM lane 372/400`)
- Applied official QM Stage-1 v6 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v6/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v4/` (`PASS`)
- Added docs:
  - `docs/QM_STAGE1_G17B_V4_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_BASELINE_GUARD.md` (v4 refresh)
  - `docs/QM_LANE_POLICY.md`, `docs/GATES.md`, `docs/REPRODUCIBILITY.md` updates
- Runtime note:
  - package completion recorded as `~5h` process window (requested tracking note).
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-2 raw vs official-v5 comparator + evidence

- Added comparator tool:
  - `scripts/tools/compare_qm_stage2_raw_vs_official_v1.py`
- Added Make target:
  - `qm_stage2_raw_vs_official`
- Generated comparison package:
  - `05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1/`
  - outputs: `profile_deltas.csv`, `summary_transition.csv`, `profile_mismatch_keys.csv`, `report.md`
- Key readout (`2500` joined profiles, no mismatch):
  - raw pass: `1750/2500`
  - official-v5 pass: `2217/2500`
  - improved `fail->pass`: `467`
  - degraded `pass->fail`: `0`
  - gate deltas: `g17` changed on `493` profiles, `g18` on `90`
- Export note:
  - `07_exports/results/RESULT_QM_STAGE2_RAW_VS_OFFICIAL_V5_V1.md`
- Scope guard:
  - tooling + diagnostics only
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-1 G17b strict failure taxonomy v1

- Added targeted taxonomy tool:
  - `scripts/tools/analyze_qm_stage1_g17b_failures_v1.py`
- Added Make target:
  - `qm_stage1_g17b_taxonomy`
- Generated taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/`
  - outputs: `g17b_fail_cases.csv`, `g17b_pass_cases.csv`, `pattern_summary.csv`, `feature_correlations.csv`, `report.md`
- Key findings on official-v5 scope (`2500` profiles):
  - `G17b` fail count: `115` (`4.60%`)
  - fail concentration: `DS-006` (`115/700`), other datasets `0`
  - dominant class: `isolated_near_threshold` (`107/115`)
  - coupled co-fails are minority (`7/115`)
- Export note:
  - `07_exports/results/RESULT_QM_STAGE1_G17B_TAXONOMY_V1.md`
- Added prereg scaffold for next candidate lane:
  - `05_validation/pre-registrations/qm-stage2-g17b-candidate-v4.md`
- Roadmap update:
  - `docs/ROADMAP.md` priority item for `G17b` candidate lane
- Scope guard:
  - tooling + diagnostics only
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-1 G18-v3 candidate promotion + official-v5 switch

- Added candidate evaluator:
  - `scripts/tools/run_qm_g18_candidate_eval_v3.py`
- Executed G18-v3 promotion package:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v3/`
  - `05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/`
- Promotion readout (`degraded=0` on all blocks):
  - primary lane: `513/600 -> 529/600`
  - attack lane: `1255/1500 -> 1316/1500`
  - holdout lane: `360/400 -> 372/400`
- Applied official QM Stage-1 v5 mapping:
  - `05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/`
- Refreshed baseline/guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/` (`PASS`)
- Added post-switch taxonomy:
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v3/`
  - fail profiles improved: `372/2500 -> 283/2500`
- Added switch/result notes:
  - `docs/QM_STAGE1_G18_V3_OFFICIAL_SWITCH.md`
  - `07_exports/results/RESULT_QM_STAGE1_G18_V3_SWITCH_V1.md`
  - `06_writing/paper-qm-stage1-g18-v3-switch-note-v1-en.md`
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-04 - GR Stage-3 v5 switch + QM Stage-1 v4 switch + stability stress pack

- Added candidate evaluators:
  - `scripts/tools/run_gr_stage3_g11_candidate_eval_v5.py`
  - `scripts/tools/run_qm_g17_candidate_eval_v3.py`
- Added QM governance applier:
  - `scripts/tools/run_qm_stage1_official_v4.py`
- Executed GR Stage-3 v5 promotion package:
  - `05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/`
  - official apply outputs:
    - `05_validation/evidence/artifacts/gr-stage3-official-v5/`
    - `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-seed500-v1/`
    - `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-holdout-v1/`
- Executed QM Stage-1 G17-v3 promotion package:
  - `05_validation/evidence/artifacts/qm-g17-candidate-v3/`
  - `05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/`
  - official apply outputs:
    - `05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/`
    - `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/`
    - `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/`
- Refreshed guards/baselines:
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v2/` (`PASS`)
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/` (`PASS`)
- Added post-switch QM Stage-1 taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/`
- Added requested stability pack outputs:
  - `05_validation/evidence/artifacts/stability-dual-sweep-v1/`
  - `05_validation/evidence/artifacts/stability-phase-diagram-chi-sigma-v1/`
  - `05_validation/evidence/artifacts/stability-scaling-test-v1/`
  - `05_validation/evidence/artifacts/stability-perturbation-torture-v1/`
  - `05_validation/evidence/artifacts/stability-long-emergence-v1/`
- Added helper script:
  - `scripts/tools/analyze_stability_phase_diagram_chi_sigma_v1.py`
- Added switch records:
  - `docs/GR_STAGE3_G11_V5_OFFICIAL_SWITCH.md`
  - `docs/QM_STAGE1_G17_V3_OFFICIAL_SWITCH.md`
- Added exports:
  - `07_exports/results/RESULT_GR_QM_STABILITY_SPRINT_V2.md`
  - `06_writing/paper-qng-gr-qm-stability-sprint-v2-en.md`
- Runtime note:
  - full coupling audit block (2500 profiles, bundled in `qm-gr-coupling-audit-v2`) was a long run (`~5h` wall-clock).
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-04 - Coupling v2 bundle + QM Stage-2 strict taxonomy + GR/QM guard rechecks

- Re-ran QM-GR coupling audit v2 chunked runners with `--resume` for all three blocks:
  - `primary_ds002_003_006_s3401_3600`
  - `attack_seed500_ds002_003_006_s3601_4100`
  - `holdout_ds004_008_s3401_3600`
- Coupling status re-confirmed:
  - completed profiles: `2500/2500`
  - G20 pass: `2500/2500`
  - GR guard pre/post: `PASS` on all blocks
- Added coupling bundle aggregator:
  - script: `scripts/tools/bundle_qm_gr_coupling_audit_v2.py`
  - Make target: `qm_gr_coupling_audit_bundle`
  - output package: `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/bundle-v1/`
- Added QM Stage-2 strict failure taxonomy:
  - script: `scripts/tools/analyze_qm_stage2_failures_v1.py`
  - Make target: `qm_stage2_taxonomy`
  - output package: `05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-v1/`
- Rechecked guards/taxonomy:
  - `gr-stage3-regression-baseline-v1/latest_check` refreshed
  - `qm-stage1-regression-baseline-v1/latest_check` refreshed
  - `qm-stage1-failure-taxonomy-v1` refreshed
  - `gr-stage3-official-v3-failure-taxonomy-v1` refreshed
- Docs:
  - `docs/REPRODUCIBILITY.md` updated with sections 49 and 50
  - `docs/GR_STAGE3_KNOWN_LIMITATIONS.md` updated with neighborhood isolation note
  - `docs/ROADMAP.md` updated with coupling-bundle and Stage-2 taxonomy priorities
- Result/export notes:
  - `07_exports/results/RESULT_GR_QM_COUPLING_CHECKPOINT_V1.md`
  - `06_writing/paper-qng-gr-qm-coupling-backbone-status-v2-en.md`
- Added focused prereg scaffold for next QM Stage-2 step:
  - `05_validation/pre-registrations/qm-stage2-g17-candidate-v1.md`
- Scope guard:
  - tooling + evidence refresh only
  - no threshold changes
  - no formula changes

## 2026-03-04 - GR Stage-3 G11 neighborhood quickcheck + theory work plan pack

- Added diagnostic runner:
  - `scripts/tools/analyze_gr_stage3_g11_fail_neighborhood_v1.py`
- Executed quickcheck package:
  - `05_validation/evidence/artifacts/gr-stage3-g11-neighborhood-v1/`
  - outputs: `fail_seed_neighborhood.csv`, `neighborhood_summary.csv`, `report.md`
- Readout:
  - remaining 3 fail anchors are isolated in `+/-5` seed windows (`1/11` fail per anchor window)
  - no local fail clustering detected around anchors
- Added result export:
  - `07_exports/results/RESULT_GR_G11_NEIGHBORHOOD_V1.md`
- Added theory execution plan (while away):
  - `docs/THEORY_WORK_PLAN_WHILE_AWAY_V1.md`
- Added short status note (EN):
  - `06_writing/paper-qng-stability-gr-qm-status-note-v1-en.md`
- Updated reproducibility index:
  - `docs/REPRODUCIBILITY.md` (new section 48)
- Scope guard:
  - diagnostic/docs only
  - no threshold changes
  - no formula changes

## 2026-03-04 - GR Stage-3 fail-closure diagnostics package (3/600 strict scope)

- Added strict diagnostic package on official Stage-3 rerun:
  - runner: `scripts/tools/analyze_stage3_failures_v1.py`
  - source: `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv`
  - output: `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/`
- Added nearest-pass neighbor comparison table:
  - `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/nearest_pass_neighbors.csv`
- Added export result note:
  - `07_exports/results/RESULT_GR_STAGE3_FAIL_CLOSURE_V1.md`
- Added mini-paper note (EN):
  - `06_writing/paper-gr-stage3-fail-closure-note-v1-en.md`
- Added prereg scaffold for next candidate cycle:
  - `05_validation/pre-registrations/gr-stage3-g11-fail-closure-v5.md`
- Readout:
  - official remains `597/600`
  - strict fail scope: `3` (`G11` only)
  - class split: `g11b_slope_instability`, `weak_corr_multi_peak`, `weak_corr_sparse_graph` (1 each)
- Scope guard:
  - no threshold changes
  - no formula changes

## 2026-03-04 - QM Stage-2 prereg full execution + resume hardening

- Added resume support for long QM prereg batches:
  - `scripts/tools/run_qm_stage1_prereg_v1.py`
  - new flag: `--resume` (skips profiles with existing per-profile summary)
- Extended Stage-2 orchestration runner:
  - `scripts/tools/run_qm_stage2_prereg_v1.py`
  - new flag: `--resume-qm-lane` (default enabled)
  - manifest now records resume behavior
- Completed full Stage-2 prereg package:
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/`
  - blocks finished:
    - primary `DS-002/003/006`, seeds `3401..3600`
    - attack `DS-002/003/006`, seeds `3601..4100`
    - holdout `DS-004/008`, seeds `3401..3600`
- QM lane readout:
  - primary: `411/600`
  - attack: `1017/1500`
  - holdout: `322/400`
  - block decisions: `HOLD` (all three)
- Coupling readout:
  - primary: `600/600` G20 pass, GR guard pre/post `PASS`
  - attack: `1500/1500` G20 pass, GR guard pre/post `PASS`
  - holdout: `400/400` G20 pass, GR guard pre/post `PASS`
- Final Stage-2 prereg package decision:
  - `HOLD` (as expected at candidate lane; no threshold/formula changes)

## 2026-03-03 - Public visibility refresh + QM Stage-2 prereg orchestration bootstrap

- Added Stage-1 bridge note:
  - `docs/QM_GR_BRIDGE_NOTE_STAGE1.md`
- Added QM Stage-2 prereg protocol doc:
  - `docs/QM_STAGE2_PREREG.md`
- Added orchestration runner:
  - `scripts/tools/run_qm_stage2_prereg_v1.py`
- Added Make targets:
  - `qm_stage2_smoke`
  - `qm_stage2_prereg`
- Updated index docs:
  - `README.md`
  - `docs/ROADMAP.md`
  - `docs/GATES.md`
  - `docs/QM_LANE_POLICY.md`
  - `docs/REPRODUCIBILITY.md`
- Executed smoke package:
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/`
  - primary smoke block: `HOLD` (`2/3` QM-lane pass), coupling `PASS`
  - attack smoke block: `HOLD` (`2/3` QM-lane pass), coupling `PASS`
  - holdout smoke block: `PASS` (`2/2` QM-lane pass), coupling `PASS`
  - combined smoke decision: `HOLD` (`1/3` blocks PASS)
- Scope guard:
  - no physics threshold/formula changes (tooling/docs only)

## 2026-03-03 - Stability convergence v6 extended audit v1 (200 seeds/block)

- Added locked prereg:
  - `05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1.md`
- Added resumable orchestrator:
  - `scripts/tools/run_stability_convergence_v6_extended_eval_v1.py`
- Added Make target:
  - `stability_convergence_v6_extended_eval`
- Executed full extended package:
  - `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1-run-record-2026-03-03.md`
- Result:
  - decision `PASS`
  - `zero_degraded_seed=true`
  - `all_v6_blocks_pass=true`
  - `holdout_shift_block_pass=true`
  - `total_degraded_seed_count=0`
  - runtime `~1h57m` (manifest)

## 2026-03-03 - Stability convergence v6 baseline+guard + telemetry + lock-in

- Added baseline builder:
  - `scripts/tools/build_stability_convergence_v6_baseline_v1.py`
- Added regression guard:
  - `scripts/tools/run_stability_convergence_v6_regression_guard_v1.py`
- Added Make targets:
  - `stability_convergence_v6_baseline_build`
  - `stability_convergence_v6_regression_guard`
  - `stability_convergence_v6_telemetry`
- Built baseline artifacts:
  - `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json`
  - `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json`
  - `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json`
- Ran latest guard:
  - `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check/`
  - decision: `PASS` (no degradation, no missing/extra, pass stays pass)
- Added telemetry (yellow-flag, non-blocking):
  - metric: positive slope seed fractions (`full`, `bulk`) per block
  - output: `latest_check/telemetry.csv`
- Added lock-in scope doc:
  - `docs/STABILITY_CONVERGENCE_V6_LOCK_IN.md`

## 2026-03-03 - Stability convergence v6 official governance switch

- Added official switch record:
  - `docs/STABILITY_CONVERGENCE_V6_OFFICIAL_SWITCH.md`
- Updated gate map to include official convergence policy:
  - `docs/GATES.md`
- Updated dual-channel governance doc references:
  - `docs/STABILITY_DUAL_CHANNELS.md`
- Governance anchors:
  - pre-tag: `pre-stability-convergence-v6-official`
  - post-tag: `stability-convergence-v6-official`
- Switch type: policy/docs only (no formula changes, no threshold tuning, no reruns).

## 2026-03-03 - Stability convergence v6 promotion audit (primary + attack + shifted holdout)

- Added promotion evaluator:
  - `scripts/tools/evaluate_stability_convergence_v6_promotion_v1.py`
- Added Make target:
  - `stability_convergence_v6_promotion_eval`
- Built audit evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/`
  - includes:
    - primary comparator (`legacy_v5like` vs `v6_candidate`)
    - attack seed block (`3601..3620`)
    - shifted holdout regime block (`3501..3520`, sparse/noise/phi-shock shifted grid)
- Promotion audit result:
  - `promotion_report.json`: `PASS`
  - `zero_degraded_seed=true`
  - `all_v6_blocks_pass=true`
  - `holdout_shift_block_pass=true`
  - `s2_all_blocks_ok=true`, `s1_ci_all_blocks_ok=true`
- Residual diagnostic note:
  - `no_positive_seed_slopes=false` (tracked as diagnostic, not promotion blocker)

## 2026-03-03 - Stability convergence v6 candidate run (dual-channel gate)

- Added v6 gate runner:
  - `scripts/tools/run_stability_convergence_gate_v6.py`
  - dual-channel decision: `S2 structural hard-pass` + `S1 energetic median-slope CI`
- Added Make targets:
  - `stability_convergence_v6_run`
  - `stability_convergence_v6_gate`
  - `stability_convergence_v6`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v6/`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v6-run-record-2026-03-03.md`
- Result:
  - decision `PASS` (`S2 pass_fraction=1.0`, `S1 full/bulk CI upper < 0`)
- Process note:
  - corrected: the `~5 hours` runtime note refers to a different earlier test batch, not this v6 run
- No physics threshold/formula changes in this update.

## 2026-03-03 - Stability dual-channel governance lock + v6 prereg skeleton

- Added dual-channel governance doc:
  - `docs/STABILITY_DUAL_CHANNELS.md`
  - defines `S1 energetic` vs `S2 structural` reporting contract
- Added candidate prereg skeleton:
  - `05_validation/pre-registrations/qng-stability-convergence-v6.md`
  - locks statistical S1 decision framing (candidate-only, not executed)
- No threshold/formula changes in this update.

## 2026-03-03 - Stability dual-attributes diagnostic (S1/S2 test)

- Added diagnostic tool:
  - `scripts/tools/analyze_stability_dual_attributes_v1.py`
- Added Make target:
  - `stability_dual_attributes`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-dual-attributes-v1/`
- Result snapshot:
  - `S2 structural` stayed saturated (`structural_profile_pass_fraction=1.0`, `structural_seed_pass_fraction=1.0`)
  - `S1 energetic` degraded (`energetic_profile_pass_fraction~0.84`, energetic seed pass `0.0`)
  - supports a two-attribute interpretation (energetic vs structural channels)

## 2026-03-03 - Stability convergence v5 candidate run (expanded levels)

- Added prereg:
  - `05_validation/pre-registrations/qng-stability-convergence-v5.md`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v5-run-record-2026-03-03.md`
- Added Make targets:
  - `stability_convergence_v5_run`
  - `stability_convergence_v5_gate`
  - `stability_convergence_v5`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v5/`
- Result:
  - decision `FAIL` (`full_seed_pass_fraction=0.45`, `bulk_seed_pass_fraction=0.00`)
  - no threshold changes; no promotion/freeze

## 2026-03-03 - Stability convergence v4 failure taxonomy (diagnostic)

- Added taxonomy tool:
  - `scripts/tools/analyze_stability_convergence_v4_failures_v1.py`
- Added Make target:
  - `stability_convergence_v4_taxonomy`
- Executed diagnostic package:
  - `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/`
- Diagnostic summary:
  - fail driver dominated by `ci_not_excluding_zero`
  - ties/support-collapse did not dominate failures in v4

## 2026-03-03 - Stability convergence v4 candidate run (robust bulk trend estimator)

- Added prereg:
  - `05_validation/pre-registrations/qng-stability-convergence-v4.md`
- Added robust bulk gate runner:
  - `scripts/tools/run_stability_convergence_gate_v4.py`
  - bulk trend policy: `Kendall tau + bootstrap CI`, pass if `tau_ci_high < 0`
- Extended stress summaries with core-stable support fields:
  - `core_stable_size`
  - `core_stable_ratio`
- Added Make targets:
  - `stability_convergence_v4_run`
  - `stability_convergence_v4_gate`
  - `stability_convergence_v4`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v4/`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v4-run-record-2026-03-03.md`
- Result:
  - decision `FAIL` (`bulk_seed_pass_fraction=0.15`, `tau_bulk_ci_high_median=0.333333`)
  - no threshold changes; no promotion/freeze

## 2026-03-03 - Stability convergence v3b candidate run (connected central component bulk metric)

- Extended stress runner outputs with connected-core diagnostics:
  - `delta_energy_rel_core_cc`
  - `energy_core_cc_start`
  - `energy_core_cc_end`
  - `core_cc_size`
  - `core_cc_ratio`
- Added prereg:
  - `05_validation/pre-registrations/qng-stability-convergence-v3b.md`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v3b-run-record-2026-03-03.md`
- Added Make targets:
  - `stability_convergence_v3b_run`
  - `stability_convergence_v3b_gate`
  - `stability_convergence_v3b`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v3b/`
- Result:
  - decision `FAIL` (`bulk_seed_pass_fraction=0.45`, `rho_bulk_median=-0.50`)
  - no threshold changes; no promotion/freeze

## 2026-03-03 - Stability convergence v3 runner + execution (Sigma-mask core-stable bulk)

- Added v3 gate runner:
  - `scripts/tools/run_stability_convergence_gate_v3.py`
- Added Make target:
  - `stability_convergence_v3_gate`
- Extended taxonomy report sentence (explicit interpretation guard):
  - `bulk_fail dominated by boundary 30->36 ...`
- Executed v3 gate package:
  - `05_validation/evidence/artifacts/stability-convergence-v3/`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v3-run-record-2026-03-03.md`
- Result:
  - decision remains `FAIL` (same aggregate as v2; no freeze/baseline promotion)

## 2026-03-03 - Stability convergence v2 taxonomy hardening (bulk definition + level map)

- Updated taxonomy tool:
  - `scripts/tools/analyze_stability_convergence_v2_failures_v1.py`
  - added explicit bulk-fail definition in report
  - added scale-localized output:
    - `bulk_fail_profile_levels.csv` (`seed x level x bulk_rho x bulk_metric`)
  - added transition localization (coarse/bulk/fine via step transitions)
- Added locked diagnostic prereg:
  - `05_validation/pre-registrations/stability-convergence-v2-diagnostic-sweep.md`
- Tightened v3 prereg governance:
  - `05_validation/pre-registrations/qng-stability-convergence-v3.md`
  - explicit single conceptual change only (`core-stable` Sigma-mask bulk)
- Updated reproducibility docs:
  - `docs/REPRODUCIBILITY.md` (section 50)

## 2026-03-03 - Stability convergence v2 bulk-fail taxonomy + diagnostic sweep + v3 prereg lock

- Added bulk-fail taxonomy tool:
  - `scripts/tools/analyze_stability_convergence_v2_failures_v1.py`
- Added diagnostic-only sweep tool:
  - `scripts/tools/run_stability_convergence_v2_diagnostic_sweep_v1.py`
- Added Make targets:
  - `stability_convergence_v2_taxonomy`
  - `stability_convergence_v2_diagnostic_sweep`
  - `stability_convergence_v2_analysis`
- Added reproducibility section:
  - `docs/REPRODUCIBILITY.md` (section 50)
- Added evidence packages:
  - `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/`
  - `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/`
- Added locked prereg (candidate-only):
  - `05_validation/pre-registrations/qng-stability-convergence-v3.md`
- Result snapshot:
  - v2 remains `FAIL` (no threshold changes)
  - bulk fail seeds: `10/20`
  - fail modes: `8` bulk-only + `2` full-and-bulk
  - diagnostic sweep is marked non-promotion/anti post-hoc

## 2026-03-03 - Stability convergence v2 (bulk/full + scaling + cross-seed)

- Added convergence-v2 prereg:
  - `05_validation/pre-registrations/qng-stability-convergence-v2.md`
- Added convergence-v2 runner:
  - `scripts/tools/run_stability_convergence_gate_v2.py`
- Added Make targets:
  - `stability_convergence_v2_run`
  - `stability_convergence_v2_gate`
  - `stability_convergence_v2`
- Added reproducibility section:
  - `docs/REPRODUCIBILITY.md` (section 49)
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v2-run-record-2026-03-03.md`
- Executed evidence package:
  - `05_validation/evidence/artifacts/stability-convergence-v2/`
- Result:
  - decision `FAIL` (full_seed_pass_fraction `0.90` pass, bulk_seed_pass_fraction `0.50` fail, rho_full_median `-0.90` pass, rho_bulk_median `-0.75` fail)
  - no threshold updates after result (anti post-hoc preserved)

## 2026-03-03 - Stability freeze v2 + Noether alignment sketch + convergence gate v1

- Added one-page freeze contract:
  - `docs/STABILITY_V2_FREEZE.md`
- Added Noether/action alignment proof sketch:
  - `03_math/derivations/qng-stability-noether-alignment-sketch-v1.md`
- Added convergence prereg contract:
  - `05_validation/pre-registrations/qng-stability-convergence-v1.md`
- Added convergence gate tooling:
  - `scripts/tools/run_stability_convergence_gate_v1.py`
- Added Make targets:
  - `stability_convergence_v1_run`
  - `stability_convergence_v1_gate`
  - `stability_convergence_v1`
- Added reproducibility section:
  - `docs/REPRODUCIBILITY.md` (section 48)
- Added run record:
  - `05_validation/pre-registrations/qng-stability-convergence-v1-run-record-2026-03-03.md`
- Executed convergence gate package:
  - `05_validation/evidence/artifacts/stability-convergence-v1/`
  - decision: `PASS` (`step_pass_fraction=0.75`, `overall_improvement=0.017213`, `support_ratio=1.055047`)

## 2026-03-03 - Stability official-v2 apply + baseline guard

- Executed official-v2 policy apply packages:
  - `05_validation/evidence/artifacts/stability-official-v2/primary_s3401/`
  - `05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401/`
  - `05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401/`
- Added baseline tooling:
  - `scripts/tools/build_stability_baseline_v1.py`
  - `scripts/tools/run_stability_regression_guard_v1.py`
- Added baseline/guard docs:
  - `docs/STABILITY_BASELINE_GUARD.md`
  - `docs/REPRODUCIBILITY.md` (section 47)
- Added Make targets:
  - `stability_baseline_build`
  - `stability_regression_guard`
- Regression guard result:
  - `05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check/`
  - decision: `PASS` (primary/attack/holdout; no profile drift; no official pass-rate degradation)

## 2026-03-03 - Stability governance switch prep (energy v2 official policy)

- Added official policy apply runner:
  - `scripts/tools/run_stability_official_v2.py`
- Added switch record:
  - `docs/STABILITY_ENERGY_V2_OFFICIAL_SWITCH.md`
- Updated gate map with stability official policy section:
  - `docs/GATES.md`
- Added apply targets:
  - `stability_official_apply_primary`
  - `stability_official_apply_attack`
  - `stability_official_apply_holdout`

## 2026-03-03 - Stability energy candidate-v2 prereg execution (primary + attack + holdout)

- Extended stability runner for prereg block support (tooling-only):
  - `scripts/tools/run_stability_stress_v1.py`
  - added block controls: `--dataset-id`, `--seed-list`, `--n-nodes-list`, `--steps-list`
  - no equation/threshold changes
- Added candidate/evaluation tooling:
  - `scripts/tools/run_stability_energy_candidate_eval_v2.py`
  - `scripts/tools/evaluate_stability_energy_promotion_v1.py`
  - `scripts/tools/summarize_stability_energy_promotion_v1.py`
- Added Make targets:
  - `stability_v2_prereg_primary`
  - `stability_v2_prereg_attack`
  - `stability_v2_prereg_holdout`
  - `stability_energy_candidate_v2_primary`
  - `stability_energy_candidate_v2_attack`
  - `stability_energy_candidate_v2_holdout`
  - `stability_energy_promotion_primary`
  - `stability_energy_promotion_attack`
  - `stability_energy_promotion_holdout`
  - `stability_energy_promotion_bundle`
  - `stability_energy_v2_full`
- Added run record:
  - `05_validation/pre-registrations/qng-stability-energy-covariant-v2-run-record-2026-03-03.md`
- Executed prereg blocks and candidate promotion checks:
  - source: `05_validation/evidence/artifacts/stability-v1-prereg-v2/`
  - candidate: `05_validation/evidence/artifacts/stability-energy-covariant-v2/`
  - promotion: `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/`
- Results:
  - primary (`n=54`): `PASS`, energy improved `10`, degraded `0`, all-pass improved `10`
  - attack (`n=108`): `PASS`, energy improved `18`, degraded `0`, all-pass improved `18`
  - holdout (`n=108`): `PASS`, energy improved `52`, degraded `0`, all-pass improved `52`
  - bundle decision: `PASS` (`3/3` blocks), non-energy degraded total `0` in all blocks

## 2026-03-03 - Stability fail taxonomy v1 + energy diagnostic split

- Extended stability stress runner diagnostics:
  - `scripts/tools/run_stability_stress_v1.py`
  - added per-case drift slopes (`global/early/late`) per 100 steps
  - added Noether-like energy track (`energy_noether_*`) for comparison vs gate energy
  - added active-regime and max-amplitude diagnostics (`Sigma/chi/phi`)
  - added static topology diagnostics (`edge_changes`, `neighbor_changes`)
- Added stability failure taxonomy tool:
  - `scripts/tools/analyze_stability_v1_failures_v1.py`
- Added make target:
  - `stability_v1_taxonomy`
- Added prereg for candidate energy-gate governance:
  - `05_validation/pre-registrations/qng-stability-energy-covariant-v2.md`
- Updated reproducibility:
  - `docs/REPRODUCIBILITY.md` (section 45)

## 2026-03-03 - Stability term lane bootstrap (QNG-v1-strict)

- Added strict stability governance contract:
  - `docs/STABILITY_V1_STRICT.md`
- Added explicit action definition:
  - `03_math/derivations/qng-stability-action-v1.md`
- Added variational update derivation:
  - `03_math/derivations/qng-stability-update-v1.md`
- Added preregistered strict protocol:
  - `05_validation/pre-registrations/qng-stability-v1-strict.md`
- Added stress runner:
  - `scripts/tools/run_stability_stress_v1.py`
- Added one-command make target:
  - `stability_v1_stress`
- Added reproducibility section:
  - `docs/REPRODUCIBILITY.md` (section 44)

## 2026-03-03 - QM Stage-1 freeze verification + full coupling audit v2 rerun

- Executed full QM-GR coupling audit v2 packages (chunked + resume-safe):
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/holdout_ds004_008_s3401_3600/`
- Rerun readout:
  - primary: `600/600` G20 pass, GR guard pre/post chunk checks all `PASS`
  - attack: `1500/1500` G20 pass, GR guard pre/post chunk checks all `PASS`
  - holdout: `400/400` G20 pass, GR guard pre/post chunk checks all `PASS`
  - total: `2500/2500` G20 pass
- Refreshed QM Stage-1 regression guard latest check:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/`
  - decision: `PASS` (primary/attack/holdout, no profile drift, no pass-rate degradation)
- Added QM Stage-1 freeze contract:
  - `docs/QM_STAGE1_FREEZE.md`
  - linked in `docs/GATES.md` and `docs/QM_LANE_POLICY.md`
- Added freeze verification commands:
  - `docs/REPRODUCIBILITY.md` (section 43)
- Runtime note:
  - full coupling audit v2 rerun duration was about `2h05` wall-clock in this environment.

## 2026-03-03 - QM-GR coupling audit v2 (chunked/resumable, timeout-safe)

- Added chunked/resumable audit runner:
  - `scripts/tools/run_qm_gr_coupling_audit_v2.py`
- Added low-artifact execution support in G20 runner:
  - `scripts/run_qng_semiclassical_v1.py`
  - new flags: `--write-artifacts/--no-write-artifacts`, `--plots/--no-plots`
- Added Makefile targets:
  - `qm_gr_coupling_audit_primary_chunked`
  - `qm_gr_coupling_audit_attack_chunked`
  - `qm_gr_coupling_audit_holdout_chunked`
- Updated reproducibility docs:
  - `docs/REPRODUCIBILITY.md` (section 42)
- Generated resumable evidence demo package:
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/resume_demo_ds002_003_006_s3401_3404/`
  - resumed from `6` to `12` profiles with `--resume`
  - final: `g20_pass=12/12`, `gr_guard_pre_all_pass=true`, `gr_guard_post_all_pass=true`

## 2026-03-03 - QM Stage-1 official-v3 apply + baseline guard + taxonomy v2

- Applied official-v3 governance packages:
  - `05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/`
- Official-v3 apply readout:
  - primary: `G18 551/600 -> 564/600`, `QM lane 513/600 -> 526/600`, `degraded=0`
  - attack: `G18 1339/1500 -> 1395/1500`, `QM lane 1255/1500 -> 1311/1500`, `degraded=0`
  - holdout: `G18 360/400 -> 372/400`, `QM lane 360/400 -> 372/400`, `degraded=0`
- Rebuilt QM Stage-1 baseline artifacts for v3 policy:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json`
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json`
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json`
- Reran regression guard:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/`
  - decision: `PASS` (all blocks, no profile drift, no pass-rate degradation)
- Generated post-switch taxonomy packages:
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/`
- Post-switch taxonomy v2 readout (`n=2500`):
  - QM lane fail profiles: `291` (previous v1: `372`)
  - dominant failing gate: `G18` (`169`), followed by `G17` (`120`)
  - dominant `G17` subgate in fail-cases: `G17b` (`115`)
  - strict `G18` fail profiles: `169`, dominant subgate `G18d`, `G20` fail count remains `0`

## 2026-03-03 - QM Stage-1 governance switch prep (G18d-v2 official policy v3)

- Added official policy applier:
  - `scripts/tools/run_qm_stage1_official_v3.py`
- Added official switch record:
  - `docs/QM_STAGE1_G18_V2_OFFICIAL_SWITCH.md`
- Updated make targets to apply v3 policy from frozen G18 candidate summaries:
  - `qm_stage1_official_apply_primary`
  - `qm_stage1_official_apply_attack`
  - `qm_stage1_official_apply_holdout`
- Kept explicit historical v2 apply targets for reproducibility:
  - `qm_stage1_official_v2_apply_primary`
  - `qm_stage1_official_v2_apply_attack`
  - `qm_stage1_official_v2_apply_holdout`
- Updated baseline/guard/taxonomy defaults to v3 policy inputs:
  - `scripts/tools/build_qm_stage1_baseline_v1.py`
  - `scripts/tools/run_qm_stage1_regression_guard_v1.py`
  - `scripts/tools/analyze_qm_stage1_failures_v1.py`
- Updated policy docs and reproducibility commands:
  - `docs/GATES.md`
  - `docs/QM_LANE_POLICY.md`
  - `docs/QM_STAGE1_BASELINE_GUARD.md`
  - `docs/ROADMAP.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-03 - QM G18d candidate-v2 hybrid prereg run (primary + attack + holdout)

- Added prereg record:
  - `05_validation/pre-registrations/qm-g18-candidate-v2.md`
- Added candidate runner:
  - `scripts/tools/run_qm_g18_candidate_eval_v2.py`
- Added promotion evaluator:
  - `scripts/tools/evaluate_qm_g18_promotion_v1.py`
- Added make targets:
  - `qm_g18_candidate_v2_primary`
  - `qm_g18_candidate_v2_attack`
  - `qm_g18_candidate_v2_holdout`
  - `qm_g18_promotion_primary`
  - `qm_g18_promotion_attack`
  - `qm_g18_promotion_holdout`
- Executed candidate + eval blocks:
  - `05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/`
- Primary (`DS-002/003/006`, seeds `3401..3600`):
  - `G18 551/600 -> 564/600`, `QM lane 513/600 -> 526/600`, `degraded=0`, decision `PASS`
- Attack (`DS-002/003/006`, seeds `3601..4100`):
  - `G18 1339/1500 -> 1395/1500`, `QM lane 1255/1500 -> 1311/1500`, `degraded=0`, decision `PASS`
- Holdout (`DS-004/008`, seeds `3401..3600`):
  - `G18 360/400 -> 372/400`, `QM lane 360/400 -> 372/400`, `degraded=0`, decision `PASS`
- DS-003 uplift check (required) passed in primary and attack.
- Process duration note:
  - end-to-end candidate+evaluation workflow took about `5 hours` wall-clock in this environment.

## 2026-03-03 - QM Stage-1 G18 failure taxonomy (v1)

- Added strict G18 taxonomy analyzer:
  - `scripts/tools/analyze_qm_stage1_g18_failures_v1.py`
- Added make target:
  - `qm_stage1_g18_taxonomy`
- Generated taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/g18_fail_cases.csv`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/g18_pass_cases.csv`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/pattern_summary_g18_subgates.csv`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/regime_summary.csv`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/feature_correlations.csv`
  - `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v1/report.md`
- Readout (`n=2500`):
  - `G18` fail profiles: `250`
  - dominant failing subgate: `G18d`
  - top fail signature: `G18D` (`249` cases)

## 2026-03-03 - QM Stage-1 failure taxonomy (post G17-v2 official)

- Added QM Stage-1 taxonomy analyzer:
  - `scripts/tools/analyze_qm_stage1_failures_v1.py`
- Added make target:
  - `qm_stage1_taxonomy`
- Generated taxonomy package:
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v1/qm_fail_cases.csv`
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v1/qm_pass_cases.csv`
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v1/pattern_summary.csv`
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v1/feature_correlations.csv`
  - `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v1/report.md`
- Post-switch readout (`n=2500`):
  - fail profiles: `372`
  - dominant failing gate: `G18`
  - dominant failing subgate: `G17b`
  - `G20` fails in QM-lane fail-cases: `0`

## 2026-03-03 - QM Stage-1 baseline + regression guard (v1)

- Added QM Stage-1 baseline builder:
  - `scripts/tools/build_qm_stage1_baseline_v1.py`
- Added QM Stage-1 regression guard:
  - `scripts/tools/run_qm_stage1_regression_guard_v1.py`
- Added make targets:
  - `qm_stage1_baseline_build`
  - `qm_stage1_regression_guard`
- Added baseline/guard reference doc:
  - `docs/QM_STAGE1_BASELINE_GUARD.md`
- Linked baseline/guard workflow in lane policy:
  - `docs/QM_LANE_POLICY.md`
- Generated baseline artifacts:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json`
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json`
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json`
- Generated latest guard check package:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/`
  - decision: `PASS` (primary/attack/holdout; no official pass-rate degradation; no profile-set drift)

## 2026-03-03 - QM Stage-1 official switch to G17-v2 policy

- Governance switch frozen with tags:
  - `pre-qm-stage1-g17-v2-official`
  - `qm-stage1-g17-v2-official`
- Added official policy applier:
  - `scripts/tools/run_qm_stage1_official_v2.py`
- Added one-command targets for official package apply:
  - `qm_stage1_official_apply_primary`
  - `qm_stage1_official_apply_attack`
  - `qm_stage1_official_apply_holdout`
- Added official switch record and policy references:
  - `docs/QM_STAGE1_G17_V2_OFFICIAL_SWITCH.md`
  - `docs/GATES.md`
  - `docs/QM_LANE_POLICY.md`
  - `docs/ROADMAP.md`
  - `docs/REPRODUCIBILITY.md`
- Generated official governance packages:
  - `05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600/`

## 2026-03-02 - QM G17-v2 candidate full prereg blocks (primary + attack + holdout)

- elapsed wall-clock runtime for this full batch (primary + attack + holdout + eval + coupling smoke): `~5 hours` on 2026-03-02.
- Added Stage-1 summary combiner:
  - `scripts/tools/combine_qm_stage1_summaries_v1.py`
- Updated candidate report framing:
  - `scripts/tools/run_qm_g17_candidate_eval_v2.py`
  - explicit single-peak/single-well interpretation for v1 global gap
  - explicit multi-peak local-gap recovery for v2
  - explicit no-threshold-tuning statement
- Executed primary block (`DS-002/003/006`, `3401..3600`) and candidate eval:
  - `05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/combined_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/primary_ds002_003_006_s3401_3600/`
  - result: `G17 439/600 -> 564/600`, `QM_LANE 411/600 -> 513/600`, `degraded=0`, decision `PASS`
- Executed attack block (`DS-002/003/006`, `3601..4100`) and candidate eval:
  - `05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/combined_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/`
  - result: `G17 1092/1500 -> 1416/1500`, `QM_LANE 1017/1500 -> 1255/1500`, `degraded=0`, decision `PASS`
- Executed holdout block (`DS-004/008`, `3401..3600`) and candidate eval:
  - `05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/combined_ds004_008_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_holdout_ds004_008_s3401_3600/`
  - `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/`
  - result: `G17 356/400 -> 400/400`, `QM_LANE 322/400 -> 360/400`, `degraded=0`, decision `PASS`
- Executed post-candidate QM-GR coupling smoke:
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-post-g17v2-smoke-v1/`
  - result: `G20 3/3`, `GR guard pre=PASS`, `GR guard post=PASS`, unchanged.

## 2026-03-02 - QM G17 candidate-v2 hybrid (DS-003 mini) + promotion eval

- Added candidate runner (governance layer, no core threshold/formula edits):
  - `scripts/tools/run_qm_g17_candidate_eval_v2.py`
- Added promotion evaluator:
  - `scripts/tools/evaluate_qm_g17_promotion_v1.py`
- Added prereg record:
  - `05_validation/pre-registrations/qm-g17-candidate-v2.md`
- Added one-command make targets:
  - `qm_stage1_ds003_mini`
  - `qm_g17_candidate_v2_ds003_mini`
  - `qm_g17_candidate_v2_primary`
  - `qm_g17_promotion_primary`
- Executed DS-003 mini candidate package (`3401..3430`):
  - `05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430/`
  - `G17: 20/30 -> 30/30`, `degraded=0`
  - `QM lane: 19/30 -> 27/30`, `degraded=0`
- Executed strict promotion eval:
  - `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/ds003_s3401_3430/`
  - decision: `PASS`

## 2026-03-02 - G17 DS-003 mini-sprint diagnosis (3401..3430)

- Added G17 diagnosis runner:
  - `scripts/tools/run_g17_diagnosis_v1.py`
- Added one-command target:
  - `Makefile` (`qm_g17_diag_ds003`)
- Executed DS-003 seed block (`3401..3430`) diagnosis package:
  - `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/`
  - result: `G17 pass=20/30`, `fail=10/30`
  - component split: `G17a fail=10`, `G17b/c/d fail=0`
  - taxonomy: `multipeak_mode_mixing=10`
- Updated reproducibility commands:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - QM-Stage-1 prereg scaffold + coupling audit tooling

- Added QM-Stage-1 prereg runner:
  - `scripts/tools/run_qm_stage1_prereg_v1.py`
- Added QM-Stage-1 evaluator:
  - `scripts/tools/evaluate_qm_stage1_prereg_v1.py`
- Added QM-GR coupling audit runner:
  - `scripts/tools/run_qm_gr_coupling_audit_v1.py`
- Added QM-Stage-1 prereg document:
  - `05_validation/pre-registrations/qm-stage1-prereg-v1.md`
- Added make targets:
  - `qm_stage1_smoke`
  - `qm_stage1_prereg`
  - `qm_stage1_eval`
  - `qm_gr_coupling_audit_smoke`
  - `qm_gr_coupling_audit`
- Updated QM lane/roadmap/repro references:
  - `docs/QM_LANE_POLICY.md`
  - `docs/ROADMAP.md`
  - `docs/GATES.md`
  - `docs/REPRODUCIBILITY.md`
- Executed smoke packages:
  - `05_validation/evidence/artifacts/qm-stage1-smoke-v1/` (`all_pass_qm_lane=2/3`)
  - `05_validation/evidence/artifacts/qm-stage1-eval-v1/smoke_ds002_003_006_s3401/` (`decision=HOLD`)
  - `05_validation/evidence/artifacts/qm-gr-coupling-audit-smoke-v1/` (`gr_guard_pre=PASS`, `gr_guard_post=PASS`)

## 2026-03-02 - Stage-3 official-v3 rerun (600) + baseline guard + fail taxonomy

- Executed full frozen Stage-3 prereg rerun package:
  - `05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v3-600-v1/`
  - prereg readout: `stage3_pass=570/600`
- Applied official-v3 governance on rerun package:
  - `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/`
  - `G11`: `581/600 -> 597/600`
  - `G12`: `585/600 -> 600/600`
  - `Stage-3`: `570/600 -> 597/600`
  - `improved_vs_v2=27`
  - `degraded_vs_v2=0`
- Refreshed Stage-3 official baseline + guard:
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json`
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json` (`PASS`)
- Added strict fail taxonomy package for remaining official-v3 fails (`3`):
  - `05_validation/evidence/artifacts/gr-stage3-official-v3-failure-taxonomy-v1/`
  - classes: `g11b_slope_instability`, `weak_corr_multi_peak`, `weak_corr_sparse_graph`
- Added known limitations note:
  - `docs/GR_STAGE3_KNOWN_LIMITATIONS.md`
- Updated Stage-3 rerun/guard/taxonomy targets to v3 paths:
  - `Makefile`

## 2026-03-02 - Stage-3 official governance switch to G11/G12 v3

- Added Stage-3 official policy applier:
  - `scripts/tools/run_gr_stage3_official_v3.py`
- Added v3 switch record:
  - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md`
- Marked v2 switch record as superseded by v3:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md`
- Applied official-v3 governance package on frozen candidate-v3 primary summary:
  - `05_validation/evidence/artifacts/gr-stage3-official-v3/`
  - `G11`: `593/600 -> 597/600`
  - `G12`: `599/600 -> 600/600`
  - `STAGE3`: `592/600 -> 597/600`
  - `degraded_vs_v2=0`
- Updated Stage-3 governance references and run targets:
  - `Makefile`
  - `docs/GATES.md`
  - `docs/GR_STATUS.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/GR_STAGE3_PREREG.md`
  - `docs/ROADMAP.md`

## 2026-03-02 - Stage-3 candidate-v3 fail-closure sprint (official-v2 baseline)

- Added Stage-3 candidate-v3 runner (`v2 -> v3`):
  - `scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py`
- Added Stage-3 candidate-v3 promotion evaluator:
  - `scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py`
- Added Stage-3 candidate-v3 prereg:
  - `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v3.md`
- Added Stage-3 official-v2 attack/holdout mapping packages:
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/`
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1/`
- Added Stage-3 candidate-v3 evidence packages:
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/`
- Added Stage-3 candidate-v3 consolidated decision report:
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/report.md`
- Primary closure result (`official-v2 -> candidate-v3`):
  - `G11`: `593/600 -> 597/600`
  - `G12`: `599/600 -> 600/600`
  - `STAGE3`: `592/600 -> 597/600`
  - `degraded_vs_v2=0`
- Attack/holdout checks:
  - attack seed500: `STAGE3 1433/1500 -> 1452/1500`, `degraded_vs_v2=0`
  - holdout: `STAGE3 398/400 -> 398/400`, `degraded_vs_v2=0`
- Updated Stage-3 target list/docs:
  - `Makefile`
  - `docs/GR_STATUS.md`
  - `docs/ROADMAP.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - Stage-3 official rerun (600) + baseline guard + fail taxonomy

- Added Stage-3 baseline/guard tooling:
  - `scripts/tools/build_gr_stage3_baseline_v1.py`
  - `scripts/tools/run_gr_stage3_regression_guard_v1.py`
- Updated Stage-3 taxonomy analyzer to support official summary schemas:
  - `scripts/tools/analyze_stage3_failures_v1.py`
- Added Stage-3 rerun/baseline/taxonomy make targets:
  - `gr_stage3_rerun_600`
  - `gr_stage3_official_rerun_apply`
  - `gr_stage3_baseline_build`
  - `gr_stage3_baseline_guard`
  - `gr_stage3_official_taxonomy`
- Executed frozen Stage-3 rerun package:
  - `05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1/`
  - prereg readout: `stage3_pass=570/600`
- Applied official-v2 on rerun package:
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/`
  - `G11`: `581/600 -> 593/600`
  - `G12`: `585/600 -> 599/600`
  - `Stage-3`: `570/600 -> 592/600`
  - `degraded_vs_v1=0`
- Refreshed Stage-3 official baseline + guard:
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json`
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json` (`PASS`)
- Added strict taxonomy package for remaining official fails (`8`):
  - `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/`
  - dominant classes: `weak_corr_multi_peak`, `weak_corr_sparse_graph`
- Updated references/docs:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md`
  - `docs/GR_STAGE3_PREREG.md`
  - `docs/GR_STATUS.md`
  - `docs/ROADMAP.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - Stage-3 governance switch definition (G11/G12 v2 policy)

- Added Stage-3 official policy applier:
  - `scripts/tools/run_gr_stage3_official_v2.py`
- Added Stage-3 official switch record:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md`
- Updated Stage-3 map/status references:
  - `docs/GATES.md`
  - `docs/GR_STATUS.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/ROADMAP.md`
  - `docs/REPRODUCIBILITY.md`
- Added Stage-3 one-command target:
  - `Makefile` (`gr_stage3_official_apply`)

## 2026-03-02 - Stage-3 prereg scaffold (v1) + full primary run + evaluation

- Added Stage-3 prereg runner with one-summary output:
  - `scripts/tools/run_gr_stage3_prereg_v1.py`
- Added Stage-3 prereg evaluator:
  - `scripts/tools/evaluate_gr_stage3_prereg_v1.py`
- Added Stage-3 strict failure taxonomy analyzer:
  - `scripts/tools/analyze_stage3_failures_v1.py`
- Added Stage-3 protocol docs:
  - `docs/GR_STAGE3_PREREG.md`
  - `05_validation/pre-registrations/gr-stage3-prereg-v1.md`
- Added Stage-3 smoke evidence package:
  - `05_validation/evidence/artifacts/gr-stage3-smoke-v1/`
  - result: `stage3_pass=3/3` (`DS-002/003/006`, seed `3401`)
- Added Stage-3 full primary evidence package:
  - `05_validation/evidence/artifacts/gr-stage3-prereg-v1/`
  - result: `stage3_pass=570/600`
- Added Stage-3 primary evaluation package:
  - `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/`
  - recommendation: `HOLD`
- Added Stage-3 failure taxonomy package:
  - `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/`
  - strict fail scope: `30` profiles
- Added Stage-3 G11/G12 candidate-v2 prereg proposal:
  - `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v2.md`
- Added Stage-3 make targets:
  - `gr_stage3_smoke`
  - `gr_stage3_prereg`
  - `gr_stage3_taxonomy`
  - `gr_stage3_eval`
- Updated references and reproducibility docs:
  - `README.md`
  - `docs/GATES.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/GR_STATUS.md`
  - `docs/REPRODUCIBILITY.md`
  - `docs/ROADMAP.md`

## 2026-03-02 - Stage-2 official governance switch to G11a-v4

- Added Stage-2 official policy applier:
  - `scripts/tools/run_gr_stage2_official_v4.py`
- Added v4 switch decision record:
  - `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`
- Marked v3 switch record as superseded by v4:
  - `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md`
- Applied official-v4 governance package on frozen official-v3 summary:
  - `05_validation/evidence/artifacts/gr-stage2-official-v4/`
  - `G11`: `594/600 -> 597/600`
  - `STAGE2`: `594/600 -> 597/600`
  - `degraded_vs_v3=0`
- Confirmed same result on rerun package:
  - `05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/`
  - `STAGE2`: `597/600`, `degraded_vs_v3=0`
- Refreshed Stage-2 baseline + latest check:
  - `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json`
  - `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.json` (`PASS`)
- Updated defaults/targets/docs to v4 paths and effective tag:
  - `Makefile`
  - `scripts/tools/build_gr_stage2_baseline_v1.py`
  - `scripts/tools/run_gr_stage2_regression_guard_v1.py`
  - `scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py`
  - `docs/GATES.md`
  - `docs/GR_STATUS.md`
  - `docs/GR_STAGE2_PREREG.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/REPRODUCIBILITY.md`
  - `README.md`
  - `docs/ROADMAP.md`

## 2026-03-02 - G11 fail-closure v3 taxonomy + G11a-v4 candidate prereg

- Added strict fail-closure taxonomy script (official-v3 6-fail scope + nearest-pass comparison):
  - `scripts/tools/analyze_gr_stage2_g11_fail_closure_v3_v1.py`
- Added G11 candidate eval runner v4 (robust rank fallback, no threshold tuning):
  - `scripts/tools/run_gr_stage2_g11_candidate_eval_v4.py`
- Added G11 v4 promotion evaluator:
  - `scripts/tools/evaluate_gr_stage2_g11_v4_promotion_v1.py`
- Added prereg definition:
  - `05_validation/pre-registrations/gr-stage2-g11-candidate-v4.md`
- Added taxonomy evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-g11-fail-closure-v3-v1/`
- Added candidate eval + promotion evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/`
  - `05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/`
- Added promotion decision summary:
  - `05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/promotion_decision.md`
- Updated reproducibility command set:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - Stage-2 full rerun confirmation on official-v3 mapping (600 profiles)

- Executed full strict rerun on frozen prereg grid:
  - `05_validation/evidence/artifacts/gr-stage2-prereg-rerun-v3-600-v1/`
  - result: `stage2_pass=570/600` (same as frozen prereg package)
- Re-applied governance v2 and v3 on rerun outputs:
  - `05_validation/evidence/artifacts/gr-stage2-official-v2-rerun-v3-600-v1/`
  - `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/`
  - official-v3 result: `594/600`, `improved_vs_v2=7`, `degraded_vs_v2=0`
- Added explicit rerun decision note:
  - `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/rerun_decision.md`
- Added consistency guard package against frozen official-v3 baseline:
  - `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/consistency_guard/`
  - decision: `PASS` with zero mismatches

## 2026-03-02 - Stage-2 official governance switch to G11a-v3

- Added Stage-2 official policy applier:
  - `scripts/tools/run_gr_stage2_official_v3.py`
- Added v3 switch decision record:
  - `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md`
- Applied official-v3 governance package on frozen official-v2 summary:
  - `05_validation/evidence/artifacts/gr-stage2-official-v3/`
  - `G11`: `587/600 -> 594/600`
  - `STAGE2`: `587/600 -> 594/600`
  - `degraded_vs_v2=0`
- Updated defaults/targets/docs for official-v3 paths and tag:
  - `Makefile`
  - `scripts/tools/build_gr_stage2_baseline_v1.py`
  - `scripts/tools/run_gr_stage2_regression_guard_v1.py`
  - `scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py`
  - `docs/GATES.md`
  - `docs/GR_STATUS.md`
  - `docs/GR_STAGE2_PREREG.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/REPRODUCIBILITY.md`
  - `README.md`
  - `docs/ROADMAP.md`

## 2026-03-02 - Stage-2 G11a-v3 candidate prereg (Poisson-source hardening)

- Added candidate eval runner:
  - `scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py`
- Added candidate promotion evaluator:
  - `scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py`
- Added prereg definition:
  - `05_validation/pre-registrations/gr-stage2-g11-candidate-v3.md`
- Stored candidate eval outputs:
  - `05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/`
  - `05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/`
- Added decision summary:
  - `05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/promotion_decision.md`
- Updated reproducibility and one-command target:
  - `docs/REPRODUCIBILITY.md`
  - `Makefile` (`gr_stage2_g11_v3_primary`)

## 2026-03-02 - Stage-2 G11 fail-only taxonomy (official-v2)

- Added strict fail-only analyzer:
  - `scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py`
- Generated evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2/g11_fail_cases.csv`
  - `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2/dataset_fail_summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2/pattern_summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2/report.md`
- Added one-command target and reproducibility section:
  - `Makefile` (`gr_stage2_g11_taxonomy_v2`)
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - Stage-2 baseline/guard refresh (official policy)

- Added Stage-2 baseline builder:
  - `scripts/tools/build_gr_stage2_baseline_v1.py`
- Added Stage-2 regression guard:
  - `scripts/tools/run_gr_stage2_regression_guard_v1.py`
- Built baseline and verified guard:
  - `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json`
  - `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.json`
- Added one-command targets:
  - `Makefile` (`gr_stage2_baseline_build`, `gr_stage2_baseline_guard`)
- Added reproducibility commands:
  - `docs/REPRODUCIBILITY.md` (Stage-2 baseline section)

## 2026-03-02 - Stage-2 official rerun (600 profiles, frozen grid)

- Executed official Stage-2 policy on full prereg grid source:
  - input: `05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv`
  - output: `05_validation/evidence/artifacts/gr-stage2-official-v2/`
- Confirmed official counts:
  - `G11`: `587/600`
  - `G12`: `600/600`
  - `STAGE2`: `587/600`
  - `improved_vs_legacy=17`, `degraded_vs_legacy=0`

## 2026-03-02 - Stage-2 official governance switch definition (G11a-v2 + G12d-v2)

- Added Stage-2 official policy applier:
  - `scripts/tools/run_gr_stage2_official_v2.py`
- Added Stage-2 switch criteria and decision policy doc:
  - `docs/GR_STAGE2_OFFICIAL_SWITCH.md`
- Updated gate/status/commitment docs for Stage-2 official mapping:
  - `docs/GATES.md`
  - `docs/GR_STAGE2_PREREG.md`
  - `docs/GR_STATUS.md`
  - `docs/GR_COMMITMENTS.md`
  - `docs/REPRODUCIBILITY.md`
  - `README.md`
  - `docs/ROADMAP.md`
- Added one-command target:
  - `Makefile` (`gr_stage2_official_apply`)

## 2026-03-02 - Stage-2 G11/G12 candidate eval v2 (high-signal correlation rule)

- Added revised candidate eval runner:
  - `scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py`
- Added revised candidate prereg:
  - `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v2.md`
- Executed and stored revised candidate eval outputs:
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/`
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/`
- Added revised promotion decision summary:
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/promotion_decision.md`
- Updated reproducibility and one-command targets:
  - `docs/REPRODUCIBILITY.md`
  - `docs/GR_STAGE2_PREREG.md`
  - `Makefile` (`gr_stage2_candidate_v2_primary`)

## 2026-03-02 - Stage-2 G11/G12 candidate eval (primary + attacks)

- Added candidate eval runner:
  - `scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py`
- Added promotion evaluator:
  - `scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py`
- Executed and stored attack grids:
  - `05_validation/evidence/artifacts/gr-stage2-attack-seed500-v1/`
  - `05_validation/evidence/artifacts/gr-stage2-attack-holdout-v1/`
- Stored candidate eval outputs:
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/`
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/`
- Added decision summary:
  - `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/promotion_decision.md`
- Updated prereg/doc tooling:
  - `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v1.md`
  - `docs/REPRODUCIBILITY.md`
  - `Makefile`

## 2026-03-02 - Stage-2 G11/G12 failure taxonomy + candidate prereg plan

- Added taxonomy analyzer:
  - `scripts/tools/analyze_gr_stage2_failures_v1.py`
- Added taxonomy evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/g11_fail_cases.csv`
  - `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/g12_fail_cases.csv`
  - `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/pattern_summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/report.md`
- Added candidate-only prereg plan (no v1 switch):
  - `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v1.md`
- Added one-command target and docs pointers:
  - `Makefile` (`gr_stage2_taxonomy`)
  - `docs/REPRODUCIBILITY.md`

## 2026-03-02 - GR Stage-2 prereg execution record (600 profiles)

- Executed frozen Stage-2 grid:
  - datasets: `DS-002/003/006`
  - seeds: `3401..3600`
  - profiles: `600`
- Added evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/dataset_summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/prereg_manifest.json`
- Updated protocol doc with execution record:
  - `docs/GR_STAGE2_PREREG.md`

## 2026-03-02 - GR Stage-2 prereg tooling + QM lane split

- Added GR Stage-2 prereg runner with one-summary CSV:
  - `scripts/tools/run_gr_stage2_prereg_v1.py`
- Added QM standalone lane runner:
  - `scripts/tools/run_qm_lane_check_v1.py`
- Added Stage-2 prereg doc:
  - `docs/GR_STAGE2_PREREG.md`
- Added QM lane separation policy:
  - `docs/QM_LANE_POLICY.md`
- Extended reproducibility command set:
  - `Makefile`
  - `docs/REPRODUCIBILITY.md`
- Updated gate/docs index pointers:
  - `docs/GATES.md`
  - `README.md`

## 2026-03-02 - GR Stage-1 internal freeze

- Added internal freeze page:
  - `docs/GR_STAGE1_FREEZE.md`
- Linked freeze page from repository index:
  - `README.md`
- Updated roadmap to reflect:
  - Stage-1 frozen scope
  - Stage-2 prereg as next GR expansion
  - QM lane separation until Stage-2 closure

## 2026-03-02 - GR status + one-command reproducibility + commitments freeze

- Added short GR status page:
  - `docs/GR_STATUS.md`
- Added frozen physics-facing scope contract:
  - `docs/GR_COMMITMENTS.md`
- Added one-command GR helper:
  - `scripts/tools/gr_one_command.py`
  - subcommands: `official-check`, `baseline-guard`, `sweep-phi`
- Added top-level `Makefile` targets:
  - `make gr_official_check DS=DS-003 SEED=3520`
  - `make gr_baseline_guard`
  - `make gr_sweep_phi`
- Updated reproducibility and repo index docs:
  - `docs/REPRODUCIBILITY.md`
  - `README.md`

## 2026-03-02 - G16b official switch to hybrid policy

- Added pre-switch safety tag:
  - `pre-g16b-hybrid-official`
- Promoted `G16b` official decision in:
  - `scripts/run_qng_action_v1.py`
  - policy: low-signal (`std(T11)/|mean(T11)| > 10`) uses `G16b-v2`; high-signal uses legacy `G16b-v1`
- Preserved audit rows in action metric artifacts:
  - `G16b` (official hybrid status)
  - `G16b-v1` (legacy)
  - `G16b-v2` (candidate component metrics)
- Updated compatibility readers:
  - `scripts/tools/run_g16b_v2_candidate_eval_v1.py`
  - `scripts/tools/run_g16_failure_taxonomy_v1.py`
  - `scripts/tools/run_g16b_split_hybrid_v1.py`
- Updated docs and logs:
  - `docs/GATES.md`
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`
  - `docs/G16B_HYBRID_PROMOTION_PREREG.md`
  - `docs/REPRODUCIBILITY.md`
  - `05_validation/results-log.md`
- Added smoke evidence package (`G13`, `G15`, `G16`):
  - `05_validation/evidence/artifacts/g16b-official-switch-smoke-v1/`

## 2026-03-02 - GR baseline/guard refresh after G16b switch

- Regenerated baseline source grid:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/run-log-grid20.txt`
  - grid definition: `DS-002/003/006 x seeds 3401..3420 x phi_scale=0.08`
- Rebuilt baseline JSONs with new effective tag:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json`
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
  - effective_tag: `gr-g16b-hybrid-official`
  - effective_commit: `077478d`
  - effective_date_utc: `2026-03-02`
- Reran regression guard against refreshed official baseline:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/`
  - result: `PASS`
  - source summary counts: `all_pass_official=53/60`, `all_pass_diagnostic=42/60`

## 2026-03-01 - G16b hybrid promotion prereg + attack validation

- Added promotion prereg doc:
  - `docs/G16B_HYBRID_PROMOTION_PREREG.md`
- Added promotion criteria evaluator:
  - `scripts/tools/evaluate_g16b_hybrid_promotion_v1.py`
- Added promotion/attack evidence outputs:
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/promotion_decision.md`
- Added attack-run summary artifacts:
  - `05_validation/evidence/artifacts/g16b-v2-candidate-attack-seed500-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-attack-holdout-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-attack-seed500-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-attack-holdout-v1/summary.csv`
- Outcome:
  - primary decision: `PASS`
  - attack seed-range decision: `PASS`
  - attack holdout decision: `PASS`
  - hybrid marked `PROMOTION-READY` (official gate switch still explicit/separate).

## 2026-03-01 - G16b hybrid split candidate prereg (low=v2, high=v1)

- Added hybrid evaluator:
  - `scripts/tools/run_g16b_split_hybrid_v1.py`
- Added evidence outputs:
  - `05_validation/evidence/artifacts/g16b-split-hybrid-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/prereg_manifest.json`
- Policy:
  - low-signal profiles use pre-registered `g16b_v2` decision
  - high-signal profiles keep legacy `g16b_v1` decision
- Result on DS-002/003/006 x seeds 3401..3600:
  - v1 fail `127/600`
  - hybrid fail `84/600`
  - improved `43`, degraded `0`
- Candidate passes prereg non-degradation checks and is marked as next promotion candidate (official gate unchanged).

## 2026-03-01 - G16b split protocol candidate (low/high signal) prereg eval

- Added split-protocol evaluator:
  - `scripts/tools/run_g16b_split_protocol_v1.py`
- Added sanity and prereg evidence:
  - `05_validation/evidence/artifacts/g16b-split-protocol-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/prereg_manifest.json`
- Frozen protocol:
  - signal index `p90(|T11|)`, threshold `0.024`
  - low gate: abs Pearson/Spearman + high-signal R2
  - high gate: abs Pearson + abs cosine + slope-only R2
- Result snapshot:
  - v1 fail `127/600`
  - split fail `100/600`
  - low-signal improved (`62 -> 20` fails), high-signal degraded (`65 -> 80` fails)
- Decision: split-v1 remains candidate-only; official G16b stays v1.

## 2026-03-01 - G16b-v2 candidate prereg evaluation (frozen)

- Added prereg evaluation runner:
  - `scripts/tools/run_g16b_v2_candidate_eval_v1.py`
- Added sanity and prereg evidence outputs:
  - `05_validation/evidence/artifacts/g16b-v2-candidate-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/prereg_manifest.json`
- Frozen protocol executed on `DS-002/003/006 x seeds 3401..3600` with `phi_scale=0.08` and strict prereg checks.
- Outcome:
  - `G16b-v1` fail `127/600`
  - `G16b-v2` fail `113/600`
  - v2 does not meet promotion rule (`600/600`), remains candidate-only.
- Updated proposal and reproducibility docs:
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-01 - G16b component diagnostics expansion + candidate proposal

- Expanded G16 taxonomy diagnostics with per-profile G16b component outputs:
  - `mean/std` for `T11` and `G11`
  - `T11` sign fractions
  - `std(T11)/|mean(T11)|`
  - Pearson and Spearman correlations
  - high-signal subset diagnostics (top 20% `|T11|`)
- Added consolidated diagnostics CSV:
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16b_component_diagnostics.csv`
- Added A/B issue-axis mapping for failing profiles in taxonomy outputs.
- Added candidate-only proposal doc (no official gate switch):
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`

## 2026-03-01 - G16 failure taxonomy diagnostics (no math changes)

- Added G16 taxonomy runner:
  - `scripts/tools/run_g16_failure_taxonomy_v1.py`
- Added taxonomy artifacts from grid20 profiles:
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_fail_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_pass_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_failure_taxonomy.md`
- Current result snapshot:
  - all observed G16 fails are `G16b`-driven (Einstein coupling R² sub-gate), with `G16a/G16c/G16d` passing.

## 2026-03-01 - GR baseline semantics split (official vs survey)

- Added explicit pass semantics in sweep/guard outputs:
  - `all_pass_official` (uses `G15b-v2`, excludes legacy-v1 effect)
  - `all_pass_diagnostic` (legacy chain including `G15` final)
- Added baseline modes in baseline builder:
  - `--mode survey` (full grid, including expected diagnostic fails)
  - `--mode official` (filtered pass-only official profiles)
- Added official baseline file:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
- Guard default baseline now points to official baseline:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Updated tracked source summary with explicit official/diagnostic pass columns:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`

## 2026-03-01 - GR stability diagnostics (no math changes)

- Added diagnostics tool for G13/G14 drift stability from sweep summaries:
  - `scripts/tools/analyze_gr_stability_v1.py`
- Added baseline-derived outputs:
  - `05_validation/evidence/artifacts/gr-stability-v1/dataset_stats.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/worst_cases.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/report.md`
- Added reproducibility command for this diagnostics pass:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-01 - GR regression guard deep baseline (grid20)

- Added deep baseline config (DS-002/003/006 x seeds 3401..3420, `PHI_SCALE=0.08`):
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json`
- Added baseline builder helper:
  - `scripts/tools/build_gr_baseline_from_sweep.py`
- `gr_baseline_grid20.json` is now maintained as survey baseline (not pass-only official baseline).
- Added provenance source summary and run-log:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/`

## 2026-03-01 - GR/PPN freeze: `gr-ppn-g15b-v2-official`

- Freeze scope: GR/PPN decision policy for G15b.
- Effective gate policy:
  - `G15b-v2` = official decision gate.
  - `G15b-v1` = legacy diagnostic-only gate.
- Promotion baseline commit: `15dd881`.
- Promotion rule source: `docs/G15B_DEFINITION_CHANGE_PROPOSAL.md`.
- Evidence baseline:
  - `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/`
  - `05_validation/evidence/artifacts/g15b-multipeak-diagnosis-v1/`

## 2026-03-01 - GR regression guard baseline (G10..G16)

- Added frozen guard baseline config:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline.json`
- Added automatic checker:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Added reproducibility command documentation:
  - `docs/REPRODUCIBILITY.md`
- Fixed `run_qng_phi_scale_sweep_v1.py` path handling for relative `--out-dir`.
