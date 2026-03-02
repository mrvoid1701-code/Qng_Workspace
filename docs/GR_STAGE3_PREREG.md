# GR Stage-3 Pre-Registration (Frozen Protocol v1)

Date: 2026-03-02  
Stage ID: `GR-Stage-3`  
Status: prereg scaffold complete; official mapping active via governance switch

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

- Stage-3 protocol remains the frozen rerun source for official mapping.
- Official Stage-3 policy is defined in:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md` (v2, historical)
  - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md` (v3, current)
- Any future official policy update must be a separate governance decision with explicit criteria and tag.
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

Candidate-v2 evaluation closure (primary + attacks):

- candidate summary roots:
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_holdout_ds004_008_s3401_3600/`
- promotion-eval roots:
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/`
- block decisions:
  - primary: `PASS` (`Stage3 570 -> 592`, improved `22`, degraded `0`)
  - attack seed500: `PASS` (`Stage3 1345 -> 1433`, improved `88`, degraded `0`)
  - attack holdout: `PASS` (`Stage3 380 -> 398`, improved `18`, degraded `0`)

All prereg constraints were satisfied in these candidate runs:

- `degraded_vs_v1 = 0`
- per-dataset non-degradation `true`
- net uplift on primary (`improved_vs_v1 > 0`)

Candidate-v3 closure and official-v3 switch:

- candidate-v3 primary/attack/holdout promotion package:
  - `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/`
- official policy application (v3):
  - `05_validation/evidence/artifacts/gr-stage3-official-v3/`
- switch record:
  - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md`
