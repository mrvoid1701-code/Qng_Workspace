# QNG-T-028 Sensitivity Scan (metric v4) — v1

**Date:** 2026-02-25  
**Script:** `scripts/run_qng_t_028_sensitivity_v4.py` (wraps `run_qng_t_028_trajectory_real.py`)  
**Prereq:** `05_validation/pre-registrations/qng-t-028-sensitivity-v4.md`  
**Dataset:** DS-005 (real flyby + Pioneer anchor)  
**Seed:** 20260225  
**Grid:** anisotropy_keep ∈ {0.2,0.3,0.4,0.5,0.6}, tau_universal ∈ {0.25,0.40,0.55} → 15 runs

## Outputs
- Artifacts per combo: `05_validation/evidence/artifacts/qng-t-028-sens-v4/comb_aniXX_tauYY/`
- Summary: `sens_summary.csv` (Δchi² per combo)
- Gates: `gate_summary.csv`
- Log: `run-log.txt`

## Gate results
- G1 (Δchi² < 0 on ≥12/15): 15 / 15 PASS  
- FINAL: PASS

All 15 runs yield the same Δchi² = -5849.293279, so the gate passes trivially.

## Limitation (important)
The wrapped runner currently does not consume the hyperparameters `anisotropy_keep` and `tau_universal`; the environment variables are recorded but not used inside `run_qng_t_028_trajectory_real.py`. Therefore the identical Δchi² across the grid reflects invariance due to unused knobs, not demonstrated sensitivity of the underlying physics model. Future v2 should plumb these parameters into the model kernel before re-running the scan.
