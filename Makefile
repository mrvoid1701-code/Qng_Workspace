PYTHON ?= python
DS ?= DS-003
SEED ?= 3520
PHI ?= 0.08

.PHONY: help gr_official_check gr_baseline_guard gr_sweep_phi gr_stage2_smoke gr_stage2_prereg qm_lane_check gr_stage2_taxonomy gr_stage2_candidate_primary gr_stage2_candidate_v2_primary gr_stage2_official_apply gr_stage2_baseline_build gr_stage2_baseline_guard gr_stage2_g11_taxonomy_v2 gr_stage2_g11_v3_primary

help:
	@echo "Targets:"
	@echo "  make gr_official_check DS=DS-003 SEED=3520 [PHI=0.08]"
	@echo "  make gr_baseline_guard"
	@echo "  make gr_sweep_phi"
	@echo "  make gr_stage2_smoke"
	@echo "  make gr_stage2_prereg"
	@echo "  make gr_stage2_taxonomy"
	@echo "  make gr_stage2_candidate_primary"
	@echo "  make gr_stage2_candidate_v2_primary"
	@echo "  make gr_stage2_official_apply"
	@echo "  make gr_stage2_baseline_build"
	@echo "  make gr_stage2_baseline_guard"
	@echo "  make gr_stage2_g11_taxonomy_v2"
	@echo "  make gr_stage2_g11_v3_primary"
	@echo "  make qm_lane_check DS=DS-002 SEED=3401"

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

gr_stage2_taxonomy:
	$(PYTHON) scripts/tools/analyze_gr_stage2_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1

gr_stage2_candidate_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v1 --strict-datasets DS-002,DS-003,DS-006

gr_stage2_candidate_v2_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v2 --strict-datasets DS-002,DS-003,DS-006

gr_stage2_official_apply:
	$(PYTHON) scripts/tools/run_gr_stage2_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v2 --policy-id gr-stage2-official-v2 --effective-tag gr-stage2-g11g12-v2-official

gr_stage2_baseline_build:
	$(PYTHON) scripts/tools/build_gr_stage2_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --baseline-id gr-stage2-official-baseline-v1 --effective-tag gr-stage2-g11g12-v2-official

gr_stage2_baseline_guard:
	$(PYTHON) scripts/tools/run_gr_stage2_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check

gr_stage2_g11_taxonomy_v2:
	$(PYTHON) scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v2

gr_stage2_g11_v3_primary:
	$(PYTHON) scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600
	$(PYTHON) scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-v3-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 5 --min-weak-corr-drop 2

qm_lane_check:
	$(PYTHON) scripts/tools/run_qm_lane_check_v1.py --dataset-id $(DS) --seed $(SEED)
