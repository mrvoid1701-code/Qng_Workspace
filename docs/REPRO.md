# REPRO

Exact commands to run from a clean clone.

## Defaults

- dataset default: `DS-002`
- seed default: `3401`
- runner policy: stdlib-only (no numpy/scipy required for these gate scripts)

## Environment

```bash
python -V
```

Optional virtual environment:

```bash
python -m venv .venv
```

## Minimal Smoke Suite

Use a clean output root to avoid touching locked evidence directories:

```bash
python scripts/run_qng_covariant_metric_v1.py --dataset-id DS-002 --seed 3401 --outdir 07_exports/smoke/g10
python scripts/run_qng_ppn_v1.py --dataset-id DS-002 --seed 3401 --outdir 07_exports/smoke/g15
python scripts/run_qng_action_v1.py --dataset-id DS-002 --seed 3401 --outdir 07_exports/smoke/g16
```

Expected: each command exits with code `0` and writes `metric_checks_*.csv` with final `pass`.

## Optional No-Artifact Dry Run

```bash
python scripts/run_qng_covariant_metric_v1.py --no-write-artifacts
```

## Regeneration Helpers

```bash
python tools/maintenance/generate_validation_plan.py
python tools/maintenance/generate_results_log.py
python tools/maintenance/generate_run_manifests.py
```
