# QM Stage-2 Prereg (v1)

Date: 2026-03-03  
Status: candidate/prereg only (not official)

## Goal

Define a frozen, anti post-hoc protocol for advancing beyond `QM-Stage-1` without changing existing physics thresholds/formulas in this step.

## Frozen Evaluation Blocks

1. Primary block
- datasets: `DS-002,DS-003,DS-006`
- seeds: `3401..3600`

2. Attack block
- datasets: `DS-002,DS-003,DS-006`
- seeds: `3601..4100`

3. Holdout block
- datasets: `DS-004,DS-008`
- seeds: `3401..3600`

## Lane Checks

Each block runs:

1. QM lane package (`G17..G20`) via `run_qm_stage1_prereg_v1.py`
2. block-level evaluator via `evaluate_qm_stage1_prereg_v1.py`
3. QM-GR coupling audit v2 (chunked) via `run_qm_gr_coupling_audit_v2.py`

## Promotion Rule (Stage-2 Candidate Gatekeeping)

For candidate promotion proposals:

1. all prereg blocks must complete with no profile mismatch,
2. no degradation versus current official Stage-1 outputs on shared profiles,
3. coupling audit must remain stable (`G20 pass` and GR guard pre/post `PASS`).

Official switch remains a separate governance commit.

## One-Command Orchestration

Runner:

- `scripts/tools/run_qm_stage2_prereg_v1.py`

Smoke:

```bash
make qm_stage2_smoke
```

Full prereg:

```bash
make qm_stage2_prereg
```

## Output Package

Default root:

- `05_validation/evidence/artifacts/qm-stage2-prereg-v1/`

Artifacts:

- `summary.csv` (block-level unified table)
- `report.md`
- `manifest.json`
- `planned_commands.txt`
- per-block subfolders (`qm_lane`, `eval`, `coupling_audit`)

## Governance Notes

1. This prereg layer is orchestration-only.
2. No threshold/formula tuning is allowed here.
3. Any gate-definition change must be candidate-first and evaluated with degraded=`0`.

