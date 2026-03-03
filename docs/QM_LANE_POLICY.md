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

## QM Stage-1 Official Policy (v3)

Effective tag:

- `qm-stage1-g18-v2-official`

Official mapping:

1. `G17` official remains inherited from prior `v2` governance outputs.
2. `G18` official uses `G18-v2` decision status from frozen candidate summaries.
3. `G17-v1` and `G18-v1` remain legacy diagnostic-only.
4. `G19/G20` remain inherited unchanged from source summaries.

Governance applier:

- `scripts/tools/run_qm_stage1_official_v3.py`

Switch record:

- `docs/QM_STAGE1_G18_V2_OFFICIAL_SWITCH.md`

## QM Stage-1 Baseline + Guard (v1)

Baseline builder:

- `scripts/tools/build_qm_stage1_baseline_v1.py`

Regression guard:

- `scripts/tools/run_qm_stage1_regression_guard_v1.py`

Reference doc:

- `docs/QM_STAGE1_BASELINE_GUARD.md`

## Stage Map

Current official stage:

- `QM-Stage-1` (frozen): `qm-stage1-g18-v2-official`
- freeze contract: `docs/QM_STAGE1_FREEZE.md`

Next stage:

- `QM-Stage-2` is not official yet (candidate/prereg lane only).
- promotion requires prereg protocol + non-degradation + coupling-audit revalidation.
- prereg protocol: `docs/QM_STAGE2_PREREG.md`
- orchestration runner: `scripts/tools/run_qm_stage2_prereg_v1.py`
