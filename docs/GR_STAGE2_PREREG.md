# GR Stage-2 Pre-Registration (Frozen Protocol)

Date: 2026-03-02  
Stage ID: `GR-Stage-2`  
Status: prereg completed; official Stage-2 governance mapping active

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

- Stage-2 does not replace Stage-1 (`G10..G16`) official guard logic automatically.
- Stage-2 official switch requires explicit criteria + separate decision record.
- QM gates (`G17..G20`) remain in a separate lane during Stage-2/Stage-2.5 hardening.

## Execution Record (2026-03-02)

Full prereg run was executed with frozen settings:

- output root: `05_validation/evidence/artifacts/gr-stage2-prereg-v1/`
- profiles: `600` (`DS-002/003/006`, seeds `3401..3600`)
- lane pass counts:
  - `lane_3p1`: `581/600`
  - `lane_strong_field`: `585/600`
  - `lane_tensor`: `600/600`
- `stage2_pass`: `570/600`

Follow-up diagnostics and candidate plan:

- taxonomy package: `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/`
- candidate prereg (no v1 switch): `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v1.md`
- candidate evaluation + promotion records: `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/`
- revised candidate prereg: `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v2.md`
- revised candidate evaluation + promotion records: `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/`

## Closure Update (2026-03-02)

Official Stage-2 governance mapping was switched after criteria closure:

- policy doc: `docs/GR_STAGE2_OFFICIAL_SWITCH.md`
- effective tag: `gr-stage2-g11g12-v2-official`
- official policy runner: `scripts/tools/run_gr_stage2_official_v2.py`
- official 600-profile rerun package: `05_validation/evidence/artifacts/gr-stage2-official-v2/`

## Governance Update (2026-03-02, G11a-v3)

Stage-2 governance was further hardened by promoting `G11a-v3` while keeping `G12d-v2` frozen:

- policy doc: `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md`
- effective tag: `gr-stage2-g11-v3-official`
- official policy runner: `scripts/tools/run_gr_stage2_official_v3.py`
- official package: `05_validation/evidence/artifacts/gr-stage2-official-v3/`

## Governance Update (2026-03-02, G11a-v4)

Stage-2 governance was hardened again by promoting `G11a-v4` while keeping `G12d-v2` frozen:

- policy doc: `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`
- effective tag: `gr-stage2-g11-v4-official`
- official policy runner: `scripts/tools/run_gr_stage2_official_v4.py`
- official package: `05_validation/evidence/artifacts/gr-stage2-official-v4/`
