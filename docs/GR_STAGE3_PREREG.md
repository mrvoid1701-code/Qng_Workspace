# GR Stage-3 Pre-Registration (Frozen Protocol v1)

Date: 2026-03-02  
Stage ID: `GR-Stage-3`  
Status: prereg scaffold active; candidate lane only

## Goal

Extend Stage-2 validation lanes with additional geometry and conservation checks, while keeping all numeric logic frozen inside existing gate runners.

Stage-3 lanes:

1. `lane_3p1_core`: `G10 + G11`
2. `lane_strong_field`: `G12`
3. `lane_tensor`: `G7`
4. `lane_geometry`: `G8`
5. `lane_conservation`: `G9`

`stage3_status` is `pass` only if all five lanes pass.

## Frozen Inputs

- datasets: `DS-002, DS-003, DS-006`
- seed range: `3401..3600`
- `phi_scale=0.08` where supported (`G10`)
- tensor config (`G7`):
  - `n_steps=80`
  - `dt=0.40`
  - `c_wave=0.15`
- conservation config (`G9`):
  - `n_steps=200`
  - `dt=0.40`
  - `c_wave=0.15`

No threshold edits and no formula edits are allowed in gate scripts for this protocol.

## One-Summary Evaluator

Runner:

- `scripts/tools/run_gr_stage3_prereg_v1.py`

Primary outputs:

- `summary.csv` (one row per dataset/seed profile)
- `dataset_summary.csv`
- `report.md`
- `prereg_manifest.json`
- `run-log.txt`

## Commands

Smoke:

```bash
python scripts/tools/run_gr_stage3_prereg_v1.py --mode smoke
```

Frozen prereg grid:

```bash
python scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
```

## Governance

- Stage-3 is a candidate expansion lane and does not overwrite Stage-1 or Stage-2 official policies.
- Any official switch must be a separate governance decision with explicit criteria and tag.
- QM gates (`G17..G20`) remain out of Stage-3 decision status and stay in a separate lane.

## Execution Record (2026-03-02)

Smoke package executed with frozen Stage-3 settings:

- output root: `05_validation/evidence/artifacts/gr-stage3-smoke-v1/`
- profiles: `3` (`DS-002/003/006`, seed `3401`)
- lane pass counts:
  - `lane_3p1_core`: `3/3`
  - `lane_strong_field`: `3/3`
  - `lane_tensor`: `3/3`
  - `lane_geometry`: `3/3`
  - `lane_conservation`: `3/3`
- `stage3_pass`: `3/3`

Full prereg package executed with frozen Stage-3 settings:

- output root: `05_validation/evidence/artifacts/gr-stage3-prereg-v1/`
- profiles: `600` (`DS-002/003/006`, seeds `3401..3600`)
- lane pass counts:
  - `lane_3p1_core`: `581/600`
  - `lane_strong_field`: `585/600`
  - `lane_tensor`: `600/600`
  - `lane_geometry`: `600/600`
  - `lane_conservation`: `600/600`
- `stage3_pass`: `570/600`

Primary-grid evaluation package:

- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/`
- recommendation: `HOLD` (candidate lane remains non-official)

Strict failure taxonomy + candidate-v2 proposal package:

- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/`
- candidate prereg: `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v2.md`
