# QNG Foundation Stability Tests V1 - Run Record (2026-03-06)

Status: executed against locked prereg `qng-foundation-stability-tests-v1.md`

## Execution

```powershell
python scripts/run_qng_el_consistency_v1.py --out-dir 05_validation/evidence/artifacts/qng-foundation-stability-v1
```

## Artifact Package

- `05_validation/evidence/artifacts/qng-foundation-stability-v1/profile_residuals.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/summary.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/report.md`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/manifest.json`
- `05_validation/evidence/artifacts/qng-foundation-stability-v1/run-log.txt`

## Snapshot

- profiles total: `432`
- profiles pass: `432`
- profiles fail: `0`

Dataset-level pass:

- `STABILITY-PRIMARY`: `162/162` pass
- `STABILITY-ATTACK`: `162/162` pass
- `STABILITY-HOLDOUT`: `108/108` pass

Residual maxima (across all profiles):

- `sigma_abs_max_max = 0.017621`
- `global_abs_max_max = 0.017621`
- `chi_abs_max_max = 0.000000`
- `phi_abs_max_max = 0.000000`

## Governance Note

No equation/threshold changes were made during execution.  
Any threshold/formula change requires prereg v2 and a fresh evidence package.
