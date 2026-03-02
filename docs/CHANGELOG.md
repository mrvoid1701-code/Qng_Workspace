# Changelog

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
