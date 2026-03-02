# QM-Stage-1 Pre-Registration (Frozen Protocol v1)

Date: 2026-03-02  
Stage ID: `QM-Stage-1`  
Status: prereg scaffold (separate lane from GR official decisions)

## Goal

Freeze an explicit QM lane package over `G17..G20` with fixed datasets/seeds and one-summary outputs, while preserving GR Stage-3 official baseline governance as independent.

## Frozen Scope

QM lanes included:

1. `G17` canonical quantization bridge (`run_qng_qm_bridge_v1.py`)
2. `G18` quantum information/emergent geometry (`run_qng_qm_info_v1.py`)
3. `G19` Unruh thermal vacuum (`run_qng_unruh_thermal_v1.py`)
4. `G20` semiclassical backreaction (`run_qng_semiclassical_v1.py`)

No threshold or formula edits are allowed in gate scripts for this protocol.

## Frozen Inputs

- primary datasets: `DS-002, DS-003, DS-006`
- primary seeds: `3401..3600`
- smoke seed: `3401`
- attack/holdout blocks will be registered as follow-up packages under this stage.

## Runner / Outputs

Runner:

- `scripts/tools/run_qm_stage1_prereg_v1.py`

Primary outputs:

- `summary.csv` (one row per dataset/seed profile)
- `dataset_summary.csv`
- `report.md`
- `prereg_manifest.json`
- `run-log.txt`

Evaluator:

- `scripts/tools/evaluate_qm_stage1_prereg_v1.py`

## Commands

Smoke:

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-stage1-smoke-v1
```

Frozen primary prereg:

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-v1
python scripts/tools/evaluate_qm_stage1_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/qm-stage1-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-stage1-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --require-zero-rc --min-all-pass-rate 0.0
```

## Coupling Audit (GR guard stability)

Audit runner:

- `scripts/tools/run_qm_gr_coupling_audit_v1.py`

Purpose:

- execute `G20` on an audit grid,
- verify Stage-3 GR baseline guard remains `PASS` before and after the audit run.

Smoke audit command:

```bash
python scripts/tools/run_qm_gr_coupling_audit_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-smoke-v1 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv
```
