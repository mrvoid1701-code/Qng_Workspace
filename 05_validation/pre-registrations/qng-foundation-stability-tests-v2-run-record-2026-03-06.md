# QNG Foundation Stability Tests V2 - Run Record (2026-03-06)

Status: executed against locked prereg `qng-foundation-stability-tests-v2.md`

## Execution

```powershell
python scripts/run_qng_el_consistency_v1.py --out-dir 05_validation/evidence/artifacts/qng-foundation-stability-v2
```

## Key V2 Method Changes

1. Residual compares independent implementations:
   - `U_current` from `run_stability_stress_v1.one_step`
   - `U_EL` from checker-local EL predictor
2. Global residual uses joint channel metric:
   - `R_joint = max(|R_sigma|, |R_chi|, |R_phi|)` per node-step
3. Nonstrict path is separated:
   - `qng-foundation-stability-v2-nonstrict`

## Artifact Package

- `05_validation/evidence/artifacts/qng-foundation-stability-v2/profile_residuals.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/summary.csv`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/report.md`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/manifest.json`
- `05_validation/evidence/artifacts/qng-foundation-stability-v2/run-log.txt`

## Snapshot

- profiles total: `432`
- profiles pass: `432`
- profiles fail: `0`

Dataset pass:

- `STABILITY-PRIMARY`: `162/162`
- `STABILITY-ATTACK`: `162/162`
- `STABILITY-HOLDOUT`: `108/108`

Observed maxima:

- `sigma_abs_max_max = 0.000000`
- `global_abs_max_max = 0.000000`
- `chi_abs_max_max = 0.000000`
- `phi_abs_max_max = 0.000000`

## Governance Note

No threshold edits were made relative to v1; only checker methodology hardening.
