# QM Lane Policy (Separated From GR Decisions)

Date: 2026-03-02

## Separation Rule

During `GR-Stage-2` and `GR-Stage-3`, QM gates are evaluated in an isolated lane and do not affect:

- `all_pass_official` for GR Stage-1,
- GR baseline guard decisions,
- GR Stage-2 prereg lane pass/fail logic.

## QM Lane Scope

- `G17` (`run_qng_qm_bridge_v1.py`)
- `G18` (`run_qng_qm_info_v1.py`)
- `G19` (`run_qng_unruh_thermal_v1.py`)
- `G20` (`run_qng_semiclassical_v1.py`)

## One-Command Runner

Runner:

- `scripts/tools/run_qm_lane_check_v1.py`

Output:

- one `summary.csv` with `G17..G20` statuses and `all_pass_qm_lane`

Example:

```bash
python scripts/tools/run_qm_lane_check_v1.py --dataset-id DS-002 --seed 3401
```

## QM-Stage-1 Prereg (v1)

Pre-registration:

- `05_validation/pre-registrations/qm-stage1-prereg-v1.md`

Runners:

- `scripts/tools/run_qm_stage1_prereg_v1.py`
- `scripts/tools/evaluate_qm_stage1_prereg_v1.py`
- `scripts/tools/run_qm_gr_coupling_audit_v1.py` (G20 + GR guard stability audit)

## Governance

- QM lane promotion criteria must be preregistered independently.
- Any GR promotion decision must reference GR-only lane artifacts.
- Any QM promotion decision must reference QM-only lane artifacts.
