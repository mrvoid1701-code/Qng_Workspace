# GR Stage-3 Prereg Registration (v1)

Date: 2026-03-02  
Protocol ID: `gr-stage3-prereg-v1`

## Intent

Start Stage-3 as a frozen candidate lane with one-summary execution over `G7/G8/G9/G10/G11/G12`, without any threshold or formula changes in gate scripts.

## Frozen Configuration

- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`
- `phi_scale=0.08` (where supported)
- tensor config (`G7`): `n_steps=80`, `dt=0.40`, `c_wave=0.15`
- conservation config (`G9`): `n_steps=200`, `dt=0.40`, `c_wave=0.15`

## Evaluator

- runner: `scripts/tools/run_gr_stage3_prereg_v1.py`
- outputs:
  - `summary.csv`
  - `dataset_summary.csv`
  - `report.md`
  - `prereg_manifest.json`
  - `run-log.txt`

## Stage-3 Decision Definition

Per profile:

- `lane_3p1_core = G10 AND G11`
- `lane_strong_field = G12`
- `lane_tensor = G7`
- `lane_geometry = G8`
- `lane_conservation = G9`
- `stage3_status = lane_3p1_core AND lane_strong_field AND lane_tensor AND lane_geometry AND lane_conservation`

## Governance Rule

- This prereg defines execution and reporting only.
- It does not auto-promote Stage-3 to official.
- Any promotion requires a separate decision doc, explicit criteria, and immutable tag.

