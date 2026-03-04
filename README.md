# QNG Workspace

Research workspace for **Quantum Node Gravity (QNG)** validation, reproducibility, and evidence packaging.

## Current Snapshot

- `GR` lane: Stage-3 official policy frozen (`gr-stage3-g11-v5-official`)
- `QM` lane: Stage-1 official policy active (`qm-stage1-g17-v3-official`)
- `Stability` lane: convergence v6 official + baseline/guard active (`stability-convergence-v6-official`)
- `QM<->GR` coupling audit v2: full primary/attack/holdout package available

Core status docs:

- `docs/GR_STATUS.md`
- `docs/QM_STAGE1_FREEZE.md`
- `docs/STABILITY_CONVERGENCE_V6_LOCK_IN.md`
- `docs/QM_GR_BRIDGE_NOTE_STAGE1.md`

## Repository Map

- `03_math/derivations/`: derivations and proof sketches
- `scripts/`: gate runners
- `scripts/tools/`: prereg evaluators, guards, taxonomy, orchestration
- `05_validation/`: test plans, prereg docs, evidence packages, manifests
- `07_exports/`: public-facing export bundles

## Quick Start

```bash
make gr_official_check DS=DS-003 SEED=3520
make qm_lane_check DS=DS-003 SEED=3520
make stability_convergence_v6_regression_guard
```

Python fallback:

```bash
python scripts/tools/gr_one_command.py official-check --dataset-id DS-003 --seed 3520
python scripts/tools/run_qm_lane_check_v1.py --dataset-id DS-003 --seed 3520
python scripts/tools/run_stability_convergence_v6_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json --seed-checks-primary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/seed_checks.csv --seed-checks-attack-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/seed_checks.csv --seed-checks-holdout-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/seed_checks.csv --report-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/report.json --report-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/report.json --report-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/report.json --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check
```

## Common Runner Flags

- `--dataset-id`
- `--seed`
- `--out-dir` / `--outdir`
- `--write-artifacts` / `--no-write-artifacts`
- `--plots` / `--no-plots`

## Governance Rules (Short)

- no threshold/formula changes in housekeeping/tooling commits
- official policy switches must be separate governance commits
- candidate promotion requires prereg + primary/attack/holdout + degraded=`0`
- all official lanes must keep regression guard `PASS`

## Documentation Index

- `docs/ROADMAP.md`
- `docs/GATES.md`
- `docs/REPRODUCIBILITY.md`
- `docs/GR_COMMITMENTS.md`
- `docs/GR_STAGE1_FREEZE.md`
- `docs/GR_STAGE2_PREREG.md`
- `docs/GR_STAGE3_PREREG.md`
- `docs/QM_LANE_POLICY.md`
- `docs/QM_STAGE1_BASELINE_GUARD.md`
- `docs/QM_STAGE2_PREREG.md`
- `docs/STABILITY_DUAL_CHANNELS.md`
- `docs/STABILITY_BASELINE_GUARD.md`

## Housekeeping Policy

- generated `run-log*`, `config*`, and `artifact-hashes*` files in evidence artifacts are ignored by default
- do not delete evidence under `05_validation/evidence/artifacts/` unless clearly regenerated and covered by policy
- keep-versioned policy is documented in `tools/keepfiles.md`

