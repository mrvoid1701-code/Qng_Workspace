PYTHON ?= python
DS ?= DS-003
SEED ?= 3520
PHI ?= 0.08

.PHONY: help gr_official_check gr_baseline_guard gr_sweep_phi gr_stage2_smoke gr_stage2_prereg qm_lane_check gr_stage2_taxonomy gr_stage2_candidate_primary gr_stage2_candidate_v2_primary

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

qm_lane_check:
	$(PYTHON) scripts/tools/run_qm_lane_check_v1.py --dataset-id $(DS) --seed $(SEED)
