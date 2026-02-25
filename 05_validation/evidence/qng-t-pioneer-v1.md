# QNG-T-PIONEER-v1 — Pioneer anomaly prediction (analytic)

**Date:** 2026-02-25  
**Script:** `scripts/run_qng_t_pioneer_v1.py`  
**Prereq:** `05_validation/pre-registrations/qng-t-pioneer-v1.md`  
**Dataset/model:** analytic (no new data), τ_flyby = 0.002051 (from T-028 v4), Σ = −GM☉/r, g ≈ δ.

## Outputs
- `05_validation/evidence/artifacts/qng-t-pioneer-v1/pioneer_prediction.csv` (r=20–70 AU, 11 samples)
- `inner_control.csv` (Mercury, Venus)
- `gate_summary.csv`
- `run-log.txt`

## Gate results
- G1 (band 6.0e-10…1.1e-9 m/s² at 20–70 AU): **FAIL** (predicted 3.04e-08…2.48e-09; too large)
- G2 (inner control <1e-12): **FAIL** (Mercury/Venus ~8.1e-05 m/s²)
- FINAL: FAIL

## Interpretation
- Using the simple lag form a_QNG = τ_flyby·|∇Σ| with τ from flyby calibration overshoots the Pioneer band by ~1–2 orders of magnitude and violates inner-planet null tests.
- This is a conservative, first-pass analytic check; no tuning applied.

## Next steps (for v2)
- Incorporate directional/anisotropy factors or decay with field strength so inner planets are suppressed while outer cruise remains in the ~10⁻¹⁰ band.
- Recompute with full lag kernel used in trajectory fits (not the flat-metric approximation) once parameters are plumbed through.
- If τ is re-estimated jointly with Pioneer data, register a new prereg (qng-t-pioneer-v2) before rerun.***
