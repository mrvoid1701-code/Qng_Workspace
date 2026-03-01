# QNG Keepfiles Policy

This file documents what must remain versioned in Git for reproducibility and public auditability.

## Must Stay Versioned

- `README.md` and all files in `docs/`
- `03_math/derivations/**`
- `scripts/run_*.py` and `scripts/_common.py`
- `05_validation/test-plan.md`
- `05_validation/results-log.md`
- `05_validation/dataset-manifest.json`
- `05_validation/dataset-manifest.md`
- `05_validation/falsifiers-per-core-claim-v1.md`
- `05_validation/evidence/*.md` (public evidence narratives)
- `05_validation/evidence/artifacts/**/metric_checks*.csv`
- `05_validation/evidence/artifacts/**/*.csv` used as published evidence tables
- `05_validation/evidence/artifacts/**/*.png` used as published evidence figures
- `05_validation/run-manifests/**`
- `05_validation/evidence/artifacts/**/run-manifest*.json` for reproducibility
- `05_validation/evidence/artifacts/**/artifact-hashes-*.json` for reproducibility where published
- `07_exports/**` that are intentionally published deliverables

## Generated Files (Do Not Track By Default)

- `05_validation/evidence/artifacts/**/run-log*.txt`
- `05_validation/evidence/artifacts/**/config*.json`
- `05_validation/evidence/artifacts/**/runs/` (regenerable per-run dumps)
- local smoke output under `07_exports/smoke/` and `07_exports/tmp/`

## Safety Rule

Do not delete evidence under `05_validation/evidence/artifacts/` unless it is confirmed auto-generated junk and already covered by `.gitignore`. Prefer moving to an archive location over deletion.
