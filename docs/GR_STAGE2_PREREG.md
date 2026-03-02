# GR Stage-2 Pre-Registration (Frozen Protocol)

Date: 2026-03-02  
Stage ID: `GR-Stage-2`  
Status: prereg/candidate lane (not official GR decision lane yet)

## Goal

Extend GR validation beyond Stage-1 weak-field scope with frozen rules for:

1. strong-field-like radial behavior checks,
2. explicit `3+1` (ADM + Einstein closure) lane checks,
3. tensor-mode propagation checks.

## Frozen Inputs

- datasets: `DS-002, DS-003, DS-006`
- seed range: `3401..3600`
- `phi_scale=0.08` where script supports it
- tensor runner fixed config:
  - `n_steps=80`
  - `dt=0.40`
  - `c_wave=0.15`

No threshold edits are allowed in gate scripts during this protocol.

## Gate Mapping (Stage-2 Lanes)

1. `lane_3p1`:
   - `G10` via `scripts/run_qng_covariant_metric_v1.py`
   - `G11` via `scripts/run_qng_einstein_eq_v1.py`
2. `lane_strong_field`:
   - `G12` via `scripts/run_qng_gr_solutions_v1.py`
3. `lane_tensor`:
   - `G7` via `scripts/run_qng_metric_dynamics_v1.py`

## One-Summary Evaluator

Runner:

- `scripts/tools/run_gr_stage2_prereg_v1.py`

Primary output:

- `summary.csv` (one row per dataset/seed profile with lane and overall Stage-2 status)

Other outputs:

- `dataset_summary.csv`
- `report.md`
- `prereg_manifest.json`
- `run-log.txt`

## Commands

Smoke:

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode smoke
```

Frozen prereg grid:

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
```

## Governance

- Stage-2 does not replace Stage-1 official GR decisions automatically.
- Promotion to official expanded GR scope requires explicit closure criteria and separate decision record after this prereg run.
- QM gates (`G17..G20`) remain in a separate lane during Stage-2.
