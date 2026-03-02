# QNG Workspace

Research workspace for **Quantum Node Gravity (QNG)** validation, reproducibility, and evidence packaging.

## Scope

- claim derivations in `03_math/derivations/`
- executable gate/test runners in `scripts/`
- validation planning/results/evidence in `05_validation/`
- public release artifacts in `07_exports/`

## Quick Start

1. Create a Python environment (stdlib-only scripts; no numpy/scipy required for gate runners).
2. Run a gate:

```bash
python scripts/run_qng_covariant_metric_v1.py --dataset-id DS-002 --seed 3401
```

3. Artifacts are written to the runner `--out-dir` (default under `05_validation/evidence/artifacts/...`).

## Common Runner Flags

- `--dataset-id` dataset selector (`DS-002` default in core runners)
- `--seed` deterministic seed (`3401` default)
- `--out-dir` or `--outdir` output directory
- `--write-artifacts` / `--no-write-artifacts`
- `--plots` / `--no-plots`

## Validation Workflow

- test matrix: `05_validation/test-plan.md`
- run journal: `05_validation/results-log.md`
- evidence narratives: `05_validation/evidence/`
- reproducibility manifests: `05_validation/run-manifests/`

## Docs

- `docs/ROADMAP.md` current stage and priorities
- `docs/REPRODUCIBILITY.md` reproducibility commands and one-command make targets
- `docs/GATES.md` gate map G1..G20 and runner mapping
- `docs/GR_STATUS.md` GR status snapshot in 60 seconds
- `docs/GR_COMMITMENTS.md` frozen physics-facing scope commitments
- `docs/GR_STAGE1_FREEZE.md` internal release freeze scope/guarantees/non-claims
- `docs/GR_STAGE2_PREREG.md` frozen prereg protocol for strong-field/3+1/tensor expansion
- `docs/GR_STAGE3_PREREG.md` frozen prereg protocol for Stage-3 lane extension (`G8/G9` added)
- `docs/GR_STAGE2_OFFICIAL_SWITCH.md` Stage-2 governance switch record (v2)
- `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md` Stage-2 governance switch record (v3)
- `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md` Stage-2 governance switch record (v4)
- `docs/QM_LANE_POLICY.md` explicit QM-lane separation policy

## Housekeeping Policy

- generated `run-log*`, `config*`, and `artifact-hashes*` files in evidence artifacts are ignored by default
- do not delete evidence under `05_validation/evidence/artifacts/`; archive/move instead
- keep-versioned policy is documented in `tools/keepfiles.md`

