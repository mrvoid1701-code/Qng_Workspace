PYTHON ?= python
DS ?= DS-003
SEED ?= 3520
PHI ?= 0.08

.PHONY: help gr_official_check gr_baseline_guard gr_sweep_phi gr_stage2_smoke gr_stage2_prereg gr_stage3_smoke gr_stage3_prereg gr_stage3_attack_seed500 gr_stage3_attack_holdout gr_stage3_taxonomy gr_stage3_eval gr_stage3_candidate_v2_primary gr_stage3_candidate_v2_attack gr_stage3_candidate_v2_holdout gr_stage3_official_apply gr_stage3_official_attack_apply gr_stage3_official_holdout_apply gr_stage3_candidate_v3_primary gr_stage3_candidate_v3_attack gr_stage3_candidate_v3_holdout gr_stage3_rerun_600 gr_stage3_official_rerun_apply gr_stage3_baseline_build gr_stage3_baseline_guard gr_stage3_official_taxonomy qm_lane_check qm_stage1_smoke qm_stage1_prereg qm_stage1_eval qm_gr_coupling_audit_smoke qm_gr_coupling_audit qm_gr_coupling_audit_primary_chunked qm_gr_coupling_audit_attack_chunked qm_gr_coupling_audit_holdout_chunked qm_gr_coupling_audit_bundle qm_g17_diag_ds003 qm_stage1_ds003_mini qm_g17_candidate_v2_ds003_mini qm_g17_candidate_v2_primary qm_g17_promotion_primary qm_stage1_official_apply_primary qm_stage1_official_apply_attack qm_stage1_official_apply_holdout qm_stage1_official_v2_apply_primary qm_stage1_official_v2_apply_attack qm_stage1_official_v2_apply_holdout qm_stage1_baseline_build qm_stage1_regression_guard qm_stage1_taxonomy qm_stage1_g17b_taxonomy qm_stage1_g18_taxonomy qm_stage2_taxonomy qm_stage2_raw_vs_official qm_g18_candidate_v2_primary qm_g18_candidate_v2_attack qm_g18_candidate_v2_holdout qm_g18_promotion_primary qm_g18_promotion_attack qm_g18_promotion_holdout gr_stage2_taxonomy gr_stage2_candidate_primary gr_stage2_candidate_v2_primary gr_stage2_official_apply gr_stage2_baseline_build gr_stage2_baseline_guard gr_stage2_g11_taxonomy_v2 gr_stage2_g11_taxonomy_v3 gr_stage2_g11_v3_primary stability_v1_stress stability_v1_taxonomy stability_convergence_v1_run stability_convergence_v1_gate stability_convergence_v1 stability_convergence_v2_run stability_convergence_v2_gate stability_convergence_v2 stability_convergence_v2_taxonomy stability_convergence_v2_diagnostic_sweep stability_convergence_v2_analysis stability_convergence_v3_gate stability_convergence_v3b_run stability_convergence_v3b_gate stability_convergence_v3b stability_convergence_v4_run stability_convergence_v4_gate stability_convergence_v4 stability_convergence_v4_taxonomy stability_convergence_v5_run stability_convergence_v5_gate stability_convergence_v5 stability_dual_attributes stability_convergence_v6_run stability_convergence_v6_gate stability_convergence_v6 stability_convergence_v6_promotion_eval stability_convergence_v6_baseline_build stability_convergence_v6_regression_guard stability_convergence_v6_telemetry stability_convergence_v6_extended_eval

help:
	@echo "Targets:"
	@echo "  make gr_official_check DS=DS-003 SEED=3520 [PHI=0.08]"
	@echo "  make gr_baseline_guard"
	@echo "  make gr_sweep_phi"
	@echo "  make gr_stage2_smoke"
	@echo "  make gr_stage2_prereg"
	@echo "  make gr_stage3_smoke"
	@echo "  make gr_stage3_prereg"
	@echo "  make gr_stage3_attack_seed500"
	@echo "  make gr_stage3_attack_holdout"
	@echo "  make gr_stage3_taxonomy"
	@echo "  make gr_stage3_eval"
	@echo "  make gr_stage3_candidate_v2_primary"
	@echo "  make gr_stage3_candidate_v2_attack"
	@echo "  make gr_stage3_candidate_v2_holdout"
	@echo "  make gr_stage3_official_apply"
	@echo "  make gr_stage3_official_attack_apply"
	@echo "  make gr_stage3_official_holdout_apply"
	@echo "  make gr_stage3_candidate_v3_primary"
	@echo "  make gr_stage3_candidate_v3_attack"
	@echo "  make gr_stage3_candidate_v3_holdout"
	@echo "  make gr_stage3_rerun_600"
	@echo "  make gr_stage3_official_rerun_apply"
	@echo "  make gr_stage3_baseline_build"
	@echo "  make gr_stage3_baseline_guard"
	@echo "  make gr_stage3_official_taxonomy"
	@echo "  make gr_stage2_taxonomy"
	@echo "  make gr_stage2_candidate_primary"
	@echo "  make gr_stage2_candidate_v2_primary"
	@echo "  make gr_stage2_official_apply"
	@echo "  make gr_stage2_baseline_build"
	@echo "  make gr_stage2_baseline_guard"
	@echo "  make gr_stage2_g11_taxonomy_v3"
	@echo "  make gr_stage2_g11_v3_primary"
	@echo "  make qm_lane_check DS=DS-002 SEED=3401"
	@echo "  make qm_stage1_smoke"
	@echo "  make qm_stage1_prereg"
	@echo "  make qm_stage1_eval"
	@echo "  make qm_stage2_smoke"
	@echo "  make qm_stage2_prereg"
	@echo "  make qm_gr_coupling_audit_smoke"
	@echo "  make qm_gr_coupling_audit"
	@echo "  make qm_gr_coupling_audit_primary_chunked"
	@echo "  make qm_gr_coupling_audit_attack_chunked"
	@echo "  make qm_gr_coupling_audit_holdout_chunked"
	@echo "  make qm_gr_coupling_audit_bundle"
	@echo "  make qm_g17_diag_ds003"
	@echo "  make qm_stage1_ds003_mini"
	@echo "  make qm_g17_candidate_v2_ds003_mini"
	@echo "  make qm_g17_candidate_v2_primary"
	@echo "  make qm_g17_promotion_primary"
	@echo "  make qm_stage1_official_apply_primary"
	@echo "  make qm_stage1_official_apply_attack"
	@echo "  make qm_stage1_official_apply_holdout"
	@echo "  make qm_stage1_baseline_build"
	@echo "  make qm_stage1_regression_guard"
	@echo "  make qm_stage1_taxonomy"
	@echo "  make qm_stage1_g17b_taxonomy"
	@echo "  make qm_stage1_g18_taxonomy"
	@echo "  make qm_stage2_taxonomy"
	@echo "  make qm_stage2_raw_vs_official"
	@echo "  make qm_g18_candidate_v2_primary"
	@echo "  make qm_g18_candidate_v2_attack"
	@echo "  make qm_g18_candidate_v2_holdout"
	@echo "  make qm_g18_promotion_primary"
	@echo "  make qm_g18_promotion_attack"
	@echo "  make qm_g18_promotion_holdout"
	@echo "  make qm_g18_candidate_v3_primary"
	@echo "  make qm_g18_candidate_v3_attack"
	@echo "  make qm_g18_candidate_v3_holdout"
	@echo "  make qm_stage1_official_v5_apply"
	@echo "  make qm_stage1_baseline_build_v3"
	@echo "  make qm_stage1_regression_guard_v3"
	@echo "  make stability_v1_stress"
	@echo "  make stability_v1_taxonomy"
	@echo "  make stability_energy_v2_full"
	@echo "  make stability_energy_promotion_primary"
	@echo "  make stability_energy_promotion_attack"
	@echo "  make stability_energy_promotion_holdout"
	@echo "  make stability_energy_promotion_bundle"
	@echo "  make stability_official_apply_primary"
	@echo "  make stability_official_apply_attack"
	@echo "  make stability_official_apply_holdout"
	@echo "  make stability_baseline_build"
	@echo "  make stability_regression_guard"
	@echo "  make stability_convergence_v1"
	@echo "  make stability_convergence_v2"
	@echo "  make stability_convergence_v2_taxonomy"
	@echo "  make stability_convergence_v2_diagnostic_sweep"
	@echo "  make stability_convergence_v2_analysis"
	@echo "  make stability_convergence_v3_gate"
	@echo "  make stability_convergence_v3b"
	@echo "  make stability_convergence_v4"
	@echo "  make stability_convergence_v4_taxonomy"
	@echo "  make stability_convergence_v5"
	@echo "  make stability_dual_attributes"
	@echo "  make stability_convergence_v6"
	@echo "  make stability_convergence_v6_promotion_eval"
	@echo "  make stability_convergence_v6_baseline_build"
	@echo "  make stability_convergence_v6_regression_guard"
	@echo "  make stability_convergence_v6_telemetry"
	@echo "  make stability_convergence_v6_extended_eval"

gr_official_check:
	$(PYTHON) scripts/tools/gr_one_command.py official-check --dataset-id $(DS) --seed $(SEED) --phi-scale $(PHI)

gr_baseline_guard:
	$(PYTHON) scripts/tools/gr_one_command.py baseline-guard

gr_sweep_phi:
	$(PYTHON) scripts/tools/gr_one_command.py sweep-phi

gr_stage2_smoke:
	$(PYTHON) scripts/tools/run_gr_stage2_prereg_v1.py --mode smoke

gr_stage2_prereg:
	$(PYTHON) scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg

gr_stage3_smoke:
	$(PYTHON) scripts/tools/run_gr_stage3_prereg_v1.py --mode smoke

gr_stage3_prereg:
	$(PYTHON) scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg

gr_stage3_attack_seed500:
	$(PYTHON) scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3601 --seed-end 4100 --out-dir 05_validation/evidence/artifacts/gr-stage3-attack-seed500-v1

gr_stage3_attack_holdout:
	$(PYTHON) scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-004,DS-008 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/gr-stage3-attack-holdout-v1

gr_stage3_taxonomy:
	$(PYTHON) scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1

gr_stage3_eval:
	$(PYTHON) scripts/tools/evaluate_gr_stage3_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-prereg-eval-v1

gr_stage3_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-g11-g12-primary-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

gr_stage3_candidate_v2_attack:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_seed500_ds002_003_006_s3601_4100
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage3-g11-g12-attack-seed500-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_candidate_v2_holdout:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_holdout_ds004_008_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage3-g11-g12-attack-holdout-v2 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_official_apply:
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3 --policy-id gr-stage3-official-v3 --effective-tag gr-stage3-g11g12-v3-official

gr_stage3_official_attack_apply:
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-attack-seed500-v1 --policy-id gr-stage3-official-v3-attack-seed500-v1 --effective-tag gr-stage3-g11g12-v3-official

gr_stage3_official_holdout_apply:
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-attack-holdout-v1 --policy-id gr-stage3-official-v3-attack-holdout-v1 --effective-tag gr-stage3-g11g12-v3-official

gr_stage3_candidate_v3_primary:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-g11-g12-primary-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

gr_stage3_candidate_v3_attack:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage3-g11-g12-attack-seed500-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_candidate_v3_holdout:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage3-g11-g12-attack-holdout-v3 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_rerun_600:
	$(PYTHON) scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v3-600-v1
	$(PYTHON) scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/rerun_ds002_003_006_s3401_3600

gr_stage3_official_rerun_apply:
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/rerun_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1 --policy-id gr-stage3-official-v3-rerun-v1 --effective-tag gr-stage3-g11g12-v3-official

gr_stage3_baseline_build:
	$(PYTHON) scripts/tools/build_gr_stage3_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --baseline-id gr-stage3-official-baseline-v1 --effective-tag gr-stage3-g11g12-v3-official

gr_stage3_baseline_guard:
	$(PYTHON) scripts/tools/run_gr_stage3_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check

gr_stage3_official_taxonomy:
	$(PYTHON) scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-failure-taxonomy-v1

gr_stage2_taxonomy:
	$(PYTHON) scripts/tools/analyze_gr_stage2_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1

gr_stage2_candidate_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v1 --strict-datasets DS-002,DS-003,DS-006

gr_stage2_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v2 --strict-datasets DS-002,DS-003,DS-006

gr_stage2_official_apply:
	$(PYTHON) scripts/tools/run_gr_stage2_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v4 --policy-id gr-stage2-official-v4 --effective-tag gr-stage2-g11-v4-official

gr_stage2_baseline_build:
	$(PYTHON) scripts/tools/build_gr_stage2_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --baseline-id gr-stage2-official-baseline-v1 --effective-tag gr-stage2-g11-v4-official

gr_stage2_baseline_guard:
	$(PYTHON) scripts/tools/run_gr_stage2_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check

gr_stage2_g11_taxonomy_v2:
	$(PYTHON) scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4

gr_stage2_g11_taxonomy_v3: gr_stage2_g11_taxonomy_v2

gr_stage2_g11_v3_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-v3-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 5 --min-weak-corr-drop 2

qm_lane_check:
	$(PYTHON) scripts/tools/run_qm_lane_check_v1.py --dataset-id $(DS) --seed $(SEED)

qm_stage1_smoke:
	$(PYTHON) scripts/tools/run_qm_stage1_prereg_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-stage1-smoke-v1

qm_stage1_prereg:
	$(PYTHON) scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-v1

qm_stage1_eval:
	$(PYTHON) scripts/tools/evaluate_qm_stage1_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/qm-stage1-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-stage1-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --require-zero-rc --min-all-pass-rate 0.0

.PHONY: qm_stage2_smoke qm_stage2_prereg

qm_stage2_smoke:
	$(PYTHON) scripts/tools/run_qm_stage2_prereg_v1.py --mode smoke --execute --with-coupling-audit --resume-qm-lane --chunk-size 25 --resume-coupling --no-write-artifacts --no-plots --out-dir 05_validation/evidence/artifacts/qm-stage2-prereg-v1

qm_stage2_prereg:
	$(PYTHON) scripts/tools/run_qm_stage2_prereg_v1.py --mode prereg --strict-prereg --execute --with-coupling-audit --resume-qm-lane --chunk-size 25 --resume-coupling --no-write-artifacts --no-plots --out-dir 05_validation/evidence/artifacts/qm-stage2-prereg-v1

qm_gr_coupling_audit_smoke:
	$(PYTHON) scripts/tools/run_qm_gr_coupling_audit_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-smoke-v1 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv

qm_gr_coupling_audit:
	$(PYTHON) scripts/tools/run_qm_gr_coupling_audit_v1.py --mode audit --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v1 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv

qm_gr_coupling_audit_primary_chunked:
	$(PYTHON) scripts/tools/run_qm_gr_coupling_audit_v2.py --ds-list DS-002,DS-003,DS-006 --seed-min 3401 --seed-max 3600 --chunk-size 25 --resume --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/primary_ds002_003_006_s3401_3600 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --no-write-artifacts --no-plots

qm_gr_coupling_audit_attack_chunked:
	$(PYTHON) scripts/tools/run_qm_gr_coupling_audit_v2.py --ds-list DS-002,DS-003,DS-006 --seed-min 3601 --seed-max 4100 --chunk-size 25 --resume --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/attack_seed500_ds002_003_006_s3601_4100 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --no-write-artifacts --no-plots

qm_gr_coupling_audit_holdout_chunked:
	$(PYTHON) scripts/tools/run_qm_gr_coupling_audit_v2.py --ds-list DS-004,DS-008 --seed-min 3401 --seed-max 3600 --chunk-size 25 --resume --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/holdout_ds004_008_s3401_3600 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --no-write-artifacts --no-plots

qm_gr_coupling_audit_bundle:
	$(PYTHON) scripts/tools/bundle_qm_gr_coupling_audit_v2.py --block-dirs 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/primary_ds002_003_006_s3401_3600,05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/attack_seed500_ds002_003_006_s3601_4100,05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/holdout_ds004_008_s3401_3600 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/bundle-v1 --bundle-id qm-gr-coupling-audit-v2-bundle

qm_g17_diag_ds003:
	$(PYTHON) scripts/tools/run_g17_diagnosis_v1.py --dataset-id DS-003 --seed-start 3401 --seed-end 3430 --out-dir 05_validation/evidence/artifacts/g17-diagnosis-ds003-v1

qm_stage1_ds003_mini:
	$(PYTHON) scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-003 --seed-start 3401 --seed-end 3430 --out-dir 05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1

qm_g17_candidate_v2_ds003_mini:
	$(PYTHON) scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430
	$(PYTHON) scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/ds003_s3401_3430 --eval-id qm-g17-ds003-mini-v2 --strict-datasets DS-003 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

qm_g17_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600

qm_g17_promotion_primary:
	$(PYTHON) scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-g17-primary-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

qm_stage1_official_v2_apply_primary:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600 --policy-id qm-stage1-official-v2 --effective-tag qm-stage1-g17-v2-official --source-policy-id qm-g17-candidate-v2-hybrid

qm_stage1_official_v2_apply_attack:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100 --policy-id qm-stage1-official-v2-attack-seed500 --effective-tag qm-stage1-g17-v2-official --source-policy-id qm-g17-candidate-v2-hybrid

qm_stage1_official_v2_apply_holdout:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600 --policy-id qm-stage1-official-v2-attack-holdout --effective-tag qm-stage1-g17-v2-official --source-policy-id qm-g17-candidate-v2-hybrid

qm_stage1_official_apply_primary:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600 --policy-id qm-stage1-official-v3 --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2

qm_stage1_official_apply_attack:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100 --policy-id qm-stage1-official-v3-attack-seed500 --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2

qm_stage1_official_apply_holdout:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600 --policy-id qm-stage1-official-v3-attack-holdout --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2

qm_stage1_baseline_build:
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block primary --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json --baseline-id qm-stage1-baseline-primary-v1 --effective-tag qm-stage1-g18-v2-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block attack --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json --baseline-id qm-stage1-baseline-attack-v1 --effective-tag qm-stage1-g18-v2-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block holdout --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json --baseline-id qm-stage1-baseline-holdout-v1 --effective-tag qm-stage1-g18-v2-official

qm_stage1_regression_guard:
	$(PYTHON) scripts/tools/run_qm_stage1_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json --summary-primary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv --summary-attack-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --summary-holdout-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check

qm_stage1_taxonomy:
	$(PYTHON) scripts/tools/analyze_qm_stage1_failures_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csvs 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-jsons 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json,05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json,05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-dir 05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2

qm_stage1_g17b_taxonomy:
	$(PYTHON) scripts/tools/analyze_qm_stage1_g17b_failures_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1

qm_stage1_g18_taxonomy:
	$(PYTHON) scripts/tools/analyze_qm_stage1_g18_failures_v1.py --official-summary-csvs 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --candidate-summary-csvs 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2

qm_stage2_taxonomy:
	$(PYTHON) scripts/tools/analyze_qm_stage2_failures_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage2-prereg-v1/primary_ds002_003_006_s3401_3600/qm_lane/summary.csv,05_validation/evidence/artifacts/qm-stage2-prereg-v1/attack_ds002_003_006_s3601_4100/qm_lane/summary.csv,05_validation/evidence/artifacts/qm-stage2-prereg-v1/holdout_ds004_008_s3401_3600/qm_lane/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage2-failure-taxonomy-v1

qm_stage2_raw_vs_official:
	$(PYTHON) scripts/tools/compare_qm_stage2_raw_vs_official_v1.py --raw-summary-csvs 05_validation/evidence/artifacts/qm-stage2-prereg-v1/primary_ds002_003_006_s3401_3600/qm_lane/summary.csv,05_validation/evidence/artifacts/qm-stage2-prereg-v1/attack_ds002_003_006_s3601_4100/qm_lane/summary.csv,05_validation/evidence/artifacts/qm-stage2-prereg-v1/holdout_ds004_008_s3401_3600/qm_lane/summary.csv --official-summary-csvs 05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage2-raw-vs-official-v5-v1

qm_g18_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600

qm_g18_candidate_v2_attack:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100

qm_g18_candidate_v2_holdout:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600

qm_g18_promotion_primary:
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-g18-primary-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift --require-uplift-datasets --uplift-datasets DS-003

qm_g18_promotion_attack:
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id qm-g18-attack-seed500-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift --require-uplift-datasets --uplift-datasets DS-003

qm_g18_promotion_holdout:
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id qm-g18-attack-holdout-v2 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift --no-require-uplift-datasets

qm_g18_candidate_v3_primary:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v3/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-g18-primary-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift --require-uplift-datasets --uplift-datasets DS-003

qm_g18_candidate_v3_attack:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_seed500_ds002_003_006_s3601_4100
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id qm-g18-attack-seed500-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift --require-uplift-datasets --uplift-datasets DS-003

qm_g18_candidate_v3_holdout:
	$(PYTHON) scripts/tools/run_qm_g18_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --candidate-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_holdout_ds004_008_s3401_3600
	$(PYTHON) scripts/tools/evaluate_qm_g18_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id qm-g18-attack-holdout-v3 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift --no-require-uplift-datasets

qm_stage1_official_v5_apply:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600 --policy-id qm-stage1-official-v5 --effective-tag qm-stage1-g18-v3-official --source-policy-id qm-g18-candidate-v3-local-ds-generalized --reference-policy-id qm-stage1-official-v4
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100 --policy-id qm-stage1-official-v5-attack-seed500 --effective-tag qm-stage1-g18-v3-official --source-policy-id qm-g18-candidate-v3-local-ds-generalized --reference-policy-id qm-stage1-official-v4
	$(PYTHON) scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600 --policy-id qm-stage1-official-v5-attack-holdout --effective-tag qm-stage1-g18-v3-official --source-policy-id qm-g18-candidate-v3-local-ds-generalized --reference-policy-id qm-stage1-official-v4

qm_stage1_baseline_build_v3:
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block primary --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_primary.json --baseline-id qm-stage1-baseline-primary-v3 --effective-tag qm-stage1-g18-v3-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block attack --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_attack.json --baseline-id qm-stage1-baseline-attack-v3 --effective-tag qm-stage1-g18-v3-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block holdout --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_holdout.json --baseline-id qm-stage1-baseline-holdout-v3 --effective-tag qm-stage1-g18-v3-official

qm_stage1_regression_guard_v3:
	$(PYTHON) scripts/tools/run_qm_stage1_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/qm_stage1_baseline_holdout.json --summary-primary-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv --summary-attack-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv --summary-holdout-csv 05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/latest_check

.PHONY: qm_g18_candidate_v3_primary qm_g18_candidate_v3_attack qm_g18_candidate_v3_holdout qm_stage1_official_v5_apply qm_stage1_baseline_build_v3 qm_stage1_regression_guard_v3

stability_v1_stress:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --out-dir 05_validation/evidence/artifacts/stability-v1

stability_v1_taxonomy:
	$(PYTHON) scripts/tools/analyze_stability_v1_failures_v1.py --summary-csv 05_validation/evidence/artifacts/stability-v1/summary.csv --out-dir 05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1

stability_v2_prereg_primary:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-PRIMARY --seed 3401 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/primary_s3401 --no-strict-exit

stability_v2_prereg_attack:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-ATTACK --seed-list 3401,4401 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/attack_s3401_4401 --no-strict-exit

stability_v2_prereg_holdout:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-HOLDOUT --seed-list 3401 --n-nodes-list 30,42 --steps-list 80 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/holdout_n30_42_s3401 --no-strict-exit

stability_energy_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/primary_s3401/summary.csv --strict-datasets STABILITY-PRIMARY --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401 --energy-threshold 0.90 --eval-id stability-energy-covariant-primary-v2

stability_energy_candidate_v2_attack:
	$(PYTHON) scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/attack_s3401_4401/summary.csv --strict-datasets STABILITY-ATTACK --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401 --energy-threshold 0.90 --eval-id stability-energy-covariant-attack-v2

stability_energy_candidate_v2_holdout:
	$(PYTHON) scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/holdout_n30_42_s3401/summary.csv --strict-datasets STABILITY-HOLDOUT --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401 --energy-threshold 0.90 --eval-id stability-energy-covariant-holdout-v2

stability_energy_promotion_primary:
	$(PYTHON) scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401/summary.csv --strict-datasets STABILITY-PRIMARY --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/primary_s3401 --eval-id stability-energy-promotion-primary-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift

stability_energy_promotion_attack:
	$(PYTHON) scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401/summary.csv --strict-datasets STABILITY-ATTACK --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/attack_s3401_4401 --eval-id stability-energy-promotion-attack-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift

stability_energy_promotion_holdout:
	$(PYTHON) scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401/summary.csv --strict-datasets STABILITY-HOLDOUT --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/holdout_n30_42_s3401 --eval-id stability-energy-promotion-holdout-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift

stability_energy_promotion_bundle:
	$(PYTHON) scripts/tools/summarize_stability_energy_promotion_v1.py --report-jsons 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/primary_s3401/report.json,05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/attack_s3401_4401/report.json,05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/holdout_n30_42_s3401/report.json --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1 --eval-id stability-energy-promotion-bundle-v1

stability_energy_v2_full: stability_v2_prereg_primary stability_v2_prereg_attack stability_v2_prereg_holdout stability_energy_candidate_v2_primary stability_energy_candidate_v2_attack stability_energy_candidate_v2_holdout stability_energy_promotion_primary stability_energy_promotion_attack stability_energy_promotion_holdout stability_energy_promotion_bundle

stability_official_apply_primary:
	$(PYTHON) scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/primary_s3401 --policy-id stability-official-v2 --effective-tag stability-energy-v2-official --source-policy-id stability-energy-covariant-v2

stability_official_apply_attack:
	$(PYTHON) scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401 --policy-id stability-official-v2-attack --effective-tag stability-energy-v2-official --source-policy-id stability-energy-covariant-v2

stability_official_apply_holdout:
	$(PYTHON) scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401 --policy-id stability-official-v2-holdout --effective-tag stability-energy-v2-official --source-policy-id stability-energy-covariant-v2

stability_baseline_build:
	$(PYTHON) scripts/tools/build_stability_baseline_v1.py --block primary --summary-csv 05_validation/evidence/artifacts/stability-official-v2/primary_s3401/summary.csv --out-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_primary.json --baseline-id stability-baseline-primary-v1 --effective-tag stability-energy-v2-official
	$(PYTHON) scripts/tools/build_stability_baseline_v1.py --block attack --summary-csv 05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401/summary.csv --out-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_attack.json --baseline-id stability-baseline-attack-v1 --effective-tag stability-energy-v2-official
	$(PYTHON) scripts/tools/build_stability_baseline_v1.py --block holdout --summary-csv 05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401/summary.csv --out-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_holdout.json --baseline-id stability-baseline-holdout-v1 --effective-tag stability-energy-v2-official

stability_regression_guard:
	$(PYTHON) scripts/tools/run_stability_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/stability-regression-baseline-v1/stability_baseline_holdout.json --summary-primary-csv 05_validation/evidence/artifacts/stability-official-v2/primary_s3401/summary.csv --summary-attack-csv 05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401/summary.csv --summary-holdout-csv 05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check

stability_convergence_v1_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V1 --seed-list 3401 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v1/raw --no-strict-exit

stability_convergence_v1_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v1.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v1/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v1 --step-tol 0.002 --min-step-pass-fraction 0.75 --min-overall-improvement 0.005 --support-worsen-factor-max 1.25

stability_convergence_v1: stability_convergence_v1_run stability_convergence_v1_gate

stability_convergence_v2_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V2 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v2/raw --no-strict-exit

stability_convergence_v2_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v2.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2 --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85

stability_convergence_v2: stability_convergence_v2_run stability_convergence_v2_gate

stability_convergence_v2_taxonomy:
	$(PYTHON) scripts/tools/analyze_stability_convergence_v2_failures_v1.py --report-json 05_validation/evidence/artifacts/stability-convergence-v2/report.json --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv --level-stats-csv 05_validation/evidence/artifacts/stability-convergence-v2/level_stats.csv --step-checks-csv 05_validation/evidence/artifacts/stability-convergence-v2/step_checks.csv --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1

stability_convergence_v2_diagnostic_sweep:
	$(PYTHON) scripts/tools/run_stability_convergence_v2_diagnostic_sweep_v1.py --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1 --mask-quantiles 0.00,0.25,0.50,0.75 --bulk-levels 30,36,42 --min-profiles-per-level 5

stability_convergence_v2_analysis: stability_convergence_v2_taxonomy stability_convergence_v2_diagnostic_sweep

stability_convergence_v3_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v3.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v3 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v3.md --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5

stability_convergence_v3b_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V3B --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v3b/raw --no-strict-exit

stability_convergence_v3b_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v3.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v3b/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v3b --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v3b.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel_core_cc --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --no-strict-exit

stability_convergence_v3b: stability_convergence_v3b_run stability_convergence_v3b_gate

stability_convergence_v4_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V4 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v4/raw --no-strict-exit

stability_convergence_v4_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v4 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v4.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit

stability_convergence_v4: stability_convergence_v4_run stability_convergence_v4_gate

stability_convergence_v4_taxonomy:
	$(PYTHON) scripts/tools/analyze_stability_convergence_v4_failures_v1.py --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v4/seed_checks.csv --level-stats-csv 05_validation/evidence/artifacts/stability-convergence-v4/level_stats.csv --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1

stability_convergence_v5_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V5 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,28,32,36,40,44,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v5/raw --no-strict-exit

stability_convergence_v5_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v5/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v5 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v5.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit

stability_convergence_v5: stability_convergence_v5_run stability_convergence_v5_gate

stability_dual_attributes:
	$(PYTHON) scripts/tools/analyze_stability_dual_attributes_v1.py --run-dirs 05_validation/evidence/artifacts/stability-convergence-v4,05_validation/evidence/artifacts/stability-convergence-v5 --out-dir 05_validation/evidence/artifacts/stability-dual-attributes-v1

stability_convergence_v6_run:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V6 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,28,32,36,40,44,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6/raw --no-strict-exit

stability_convergence_v6_gate:
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit

stability_convergence_v6: stability_convergence_v6_run stability_convergence_v6_gate

stability_convergence_v6_promotion_eval:
	$(PYTHON) scripts/tools/evaluate_stability_convergence_v6_promotion_v1.py --audit-root 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1 --blocks primary_s3401_3420,attack_seed3601_3620,holdout_regime_shift_s3501_3520 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1 --eval-id stability-convergence-v6-promotion-eval-v1

stability_convergence_v6_baseline_build:
	$(PYTHON) scripts/tools/build_stability_convergence_v6_baseline_v1.py --block primary --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json --baseline-id stability-convergence-v6-baseline-primary-v1 --effective-tag stability-convergence-v6-official
	$(PYTHON) scripts/tools/build_stability_convergence_v6_baseline_v1.py --block attack --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json --baseline-id stability-convergence-v6-baseline-attack-v1 --effective-tag stability-convergence-v6-official
	$(PYTHON) scripts/tools/build_stability_convergence_v6_baseline_v1.py --block holdout --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json --baseline-id stability-convergence-v6-baseline-holdout-v1 --effective-tag stability-convergence-v6-official

stability_convergence_v6_regression_guard:
	$(PYTHON) scripts/tools/run_stability_convergence_v6_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json --seed-checks-primary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/seed_checks.csv --seed-checks-attack-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/seed_checks.csv --seed-checks-holdout-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/seed_checks.csv --report-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/report.json --report-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/report.json --report-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/report.json --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check

stability_convergence_v6_telemetry: stability_convergence_v6_regression_guard

stability_convergence_v6_extended_eval:
	$(PYTHON) scripts/tools/run_stability_convergence_v6_extended_eval_v1.py --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-extended-v1 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1.md --resume

.PHONY: stability_v2_prereg_primary stability_v2_prereg_attack stability_v2_prereg_holdout stability_energy_candidate_v2_primary stability_energy_candidate_v2_attack stability_energy_candidate_v2_holdout stability_energy_promotion_primary stability_energy_promotion_attack stability_energy_promotion_holdout stability_energy_promotion_bundle stability_energy_v2_full stability_official_apply_primary stability_official_apply_attack stability_official_apply_holdout stability_baseline_build stability_regression_guard stability_convergence_v1_run stability_convergence_v1_gate stability_convergence_v1 stability_convergence_v2_run stability_convergence_v2_gate stability_convergence_v2 stability_convergence_v2_taxonomy stability_convergence_v2_diagnostic_sweep stability_convergence_v2_analysis stability_convergence_v3_gate stability_convergence_v3b_run stability_convergence_v3b_gate stability_convergence_v3b stability_convergence_v4_run stability_convergence_v4_gate stability_convergence_v4 stability_convergence_v4_taxonomy stability_convergence_v5_run stability_convergence_v5_gate stability_convergence_v5 stability_dual_attributes stability_convergence_v6_run stability_convergence_v6_gate stability_convergence_v6 stability_convergence_v6_promotion_eval stability_convergence_v6_baseline_build stability_convergence_v6_regression_guard stability_convergence_v6_telemetry stability_convergence_v6_extended_eval

.PHONY: gr_stage3_candidate_v5_primary gr_stage3_candidate_v5_attack gr_stage3_candidate_v5_holdout gr_stage3_official_v5_apply qm_g17_candidate_v3_primary qm_g17_candidate_v3_attack qm_g17_candidate_v3_holdout qm_stage1_official_v4_apply qm_stage1_baseline_build_v2 qm_stage1_regression_guard_v2 qm_stage1_taxonomy_v2 stability_dual_sweep_v1 stability_phase_diagram_chi_sigma_v1 stability_scaling_test_v1 stability_perturbation_torture_v1 stability_long_emergence_v1 stability_requested_pack_v1

gr_stage3_candidate_v5_primary:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_candidate_eval_v5.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-g11-primary-v5 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_candidate_v5_attack:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_candidate_eval_v5.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_seed500_ds002_003_006_s3601_4100
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage3-g11-attack-seed500-v5 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_candidate_v5_holdout:
	$(PYTHON) scripts/tools/run_gr_stage3_g11_candidate_eval_v5.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_holdout_ds004_008_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage3_g11_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage3-g11-attack-holdout-v5 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

gr_stage3_official_v5_apply:
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v5 --policy-id gr-stage3-official-v5 --effective-tag gr-stage3-g11-v5-official
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v5-attack-seed500-v1 --policy-id gr-stage3-official-v5-attack-seed500-v1 --effective-tag gr-stage3-g11-v5-official
	$(PYTHON) scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-candidate-v5/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v5-attack-holdout-v1 --policy-id gr-stage3-official-v5-attack-holdout-v1 --effective-tag gr-stage3-g11-v5-official

qm_g17_candidate_v3_primary:
	$(PYTHON) scripts/tools/run_qm_g17_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-g17-primary-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

qm_g17_candidate_v3_attack:
	$(PYTHON) scripts/tools/run_qm_g17_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100
	$(PYTHON) scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id qm-g17-attack-seed500-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

qm_g17_candidate_v3_holdout:
	$(PYTHON) scripts/tools/run_qm_g17_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600
	$(PYTHON) scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id qm-g17-attack-holdout-v3 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

qm_stage1_official_v4_apply:
	$(PYTHON) scripts/tools/run_qm_stage1_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600 --policy-id qm-stage1-official-v4 --effective-tag qm-stage1-g17-v3-official --source-policy-id qm-g17-candidate-v3-hybrid-generalized --reference-policy-id qm-stage1-official-v3
	$(PYTHON) scripts/tools/run_qm_stage1_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100 --policy-id qm-stage1-official-v4-attack-seed500 --effective-tag qm-stage1-g17-v3-official --source-policy-id qm-g17-candidate-v3-hybrid-generalized --reference-policy-id qm-stage1-official-v3
	$(PYTHON) scripts/tools/run_qm_stage1_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600 --policy-id qm-stage1-official-v4-attack-holdout --effective-tag qm-stage1-g17-v3-official --source-policy-id qm-g17-candidate-v3-hybrid-generalized --reference-policy-id qm-stage1-official-v3

qm_stage1_baseline_build_v2:
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block primary --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_primary.json --baseline-id qm-stage1-baseline-primary-v2 --effective-tag qm-stage1-g17-v3-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block attack --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_attack.json --baseline-id qm-stage1-baseline-attack-v2 --effective-tag qm-stage1-g17-v3-official
	$(PYTHON) scripts/tools/build_qm_stage1_baseline_v1.py --block holdout --summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-json 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_holdout.json --baseline-id qm-stage1-baseline-holdout-v2 --effective-tag qm-stage1-g17-v3-official

qm_stage1_regression_guard_v2:
	$(PYTHON) scripts/tools/run_qm_stage1_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/qm_stage1_baseline_holdout.json --summary-primary-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv --summary-attack-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --summary-holdout-csv 05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/latest_check

qm_stage1_taxonomy_v2:
	$(PYTHON) scripts/tools/analyze_qm_stage1_failures_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --metrics-summary-csvs 05_validation/evidence/artifacts/qm-g17-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-g17-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --promotion-report-jsons 05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json,05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json,05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json --out-dir 05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2

stability_dual_sweep_v1:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-DUAL-SWEEP-V1 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410 --n-nodes-list 30,36,42 --steps-list 80 --out-dir 05_validation/evidence/artifacts/stability-dual-sweep-v1 --no-strict-exit

stability_phase_diagram_chi_sigma_v1:
	$(PYTHON) scripts/tools/analyze_stability_phase_diagram_chi_sigma_v1.py --summary-csv 05_validation/evidence/artifacts/stability-dual-sweep-v1/summary.csv --out-dir 05_validation/evidence/artifacts/stability-phase-diagram-chi-sigma-v1

stability_scaling_test_v1:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-SCALING-TEST-V1 --seed-list 3501,3502,3503,3504,3505,3506,3507,3508,3509,3510 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-scaling-test-v1/raw --no-strict-exit
	$(PYTHON) scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-scaling-test-v1/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-scaling-test-v1/v6_candidate --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit

stability_perturbation_torture_v1:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-TORTURE-V1 --seed-list 3601,3602,3603,3604,3605,3606,3607,3608,3609,3610 --n-nodes-list 36 --steps-list 100 --edge-prob-grid 0.03,0.05,0.08 --chi-scale-grid 0.20,2.00,3.00 --noise-grid 0.05,0.10 --phi-shock-grid 0.80,1.20 --out-dir 05_validation/evidence/artifacts/stability-perturbation-torture-v1 --no-strict-exit
	$(PYTHON) scripts/tools/analyze_stability_v1_failures_v1.py --summary-csv 05_validation/evidence/artifacts/stability-perturbation-torture-v1/summary.csv --out-dir 05_validation/evidence/artifacts/stability-perturbation-torture-v1/failure-taxonomy

stability_long_emergence_v1:
	$(PYTHON) scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-LONG-EMERGENCE-V1 --seed-list 3701,3702,3703 --n-nodes-list 42 --steps-list 300 --edge-prob-grid 0.12,0.25 --chi-scale-grid 1.00,1.50 --noise-grid 0.00,0.02 --phi-shock-grid 0.00,0.40 --out-dir 05_validation/evidence/artifacts/stability-long-emergence-v1 --no-strict-exit

stability_requested_pack_v1: stability_dual_sweep_v1 stability_phase_diagram_chi_sigma_v1 stability_scaling_test_v1 stability_perturbation_torture_v1 stability_long_emergence_v1
