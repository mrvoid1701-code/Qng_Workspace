# RESULT: Real-Data Status (D3/D4 First Pass, V1)

Date: 2026-03-06

## Scope

This note summarizes the current real-data lane status from artifacts:

- `d3-attack-v1`
- `d3b-candidate-v1`
- `d3c-spectral-v1`
- `d4-rotation-real-v1`
- `d4b-rotation-sigma-real-v1`
- `d4c-rotation-kernel-v1`

## Executive Verdict

- **Numeric consistency:** strong (already established)
- **Real-data discriminative power:** **not closed yet**
- **Go/No-Go (current):** **HOLD**

Reason: D3 family currently shows weak discrimination of QNG versus other smooth fields, and D4 family does not yet beat MOND on rotation-curve fits.

## Per-Test Outcomes

1. `d3-attack-v1` -> **FAIL (discriminant gate)**
- Key finding: all controls pass (`C1..C5`), including pure noise variants in this setup.
- Interpretation: current D3 behavior is tautology-like (insufficiently selective for QNG-specific structure).

2. `d3b-candidate-v1` -> **FAIL (cross-margin)**
- Configured margin threshold: `0.05`
- Measured QNG-vs-noise gap at anisotropy=1.0: `0.0158004406`
- Cross rows: `d3b_cross_pass=False` throughout.
- Interpretation: candidate did not produce robust separation.

3. `d3c-spectral-v1` -> **PARTIAL PASS / HOLD**
- Strong smooth-vs-noise separation observed:
  - `dirichlet_ratio_noise_over_qng = 11.6478`
  - `spectral_ratio_K10`: QNG `0.8902` vs noise `0.0432`
- But hypothesis text confirms: does **not** separate QNG from other smooth controls.
- Interpretation: useful as regularity detector, not yet QNG-specific discriminator.

4. `d4-rotation-real-v1` -> **FAIL (model ranking)**
- `chi2_per_n`: null `302.46`, MOND `94.43`, QNG-gradient `302.38`
- `delta_chi2_qng_minus_mond = 705131.49`
- Verdict in artifact: `MOND bate QNG gradient`.

5. `d4b-rotation-sigma-real-v1` -> **FAIL (model ranking)**
- `chi2_per_n`: null `302.46`, MOND `94.43`, QNG-S1 `226.22`
- Improves over null but remains far above MOND.
- `delta_chi2_qng_minus_mond = 446889.30`.

6. `d4c-rotation-kernel-v1` -> **HOLD (improves null, not competitive vs MOND)**
- `chi2_per_n`: null `302.46`, MOND `94.43`, QNG-kernel `254.72`
- Improvement vs null: `15.79%`
- Still far from MOND (`delta_chi2_vs_mond = 543516.74`).

## Consolidated Decision

- Real-data lane is **promising structurally** (kernel/spectral signals), but **not yet competitive** on primary physical fit target (rotation curves vs MOND baseline).
- Current status for publication-grade claim: **HOLD**.

## Immediate Next Step (No post-hoc tuning)

Run a preregistered `D4-Stage-2` block with fixed protocol:

1. fixed train/validation split by galaxy ID,
2. fixed complexity budget (AIC/BIC constrained),
3. fixed candidate set (no threshold moving),
4. summary table with `chi2_per_n`, `delta_chi2`, `delta_AIC`, `delta_BIC`.

If Stage-2 still cannot approach MOND ranking, treat rotation-curve lane as limitation in current theory version.

## Evidence Paths

- `05_validation/evidence/artifacts/d3-attack-v1/`
- `05_validation/evidence/artifacts/d3b-candidate-v1/`
- `05_validation/evidence/artifacts/d3c-spectral-v1/`
- `05_validation/evidence/artifacts/d4-rotation-real-v1/`
- `05_validation/evidence/artifacts/d4b-rotation-sigma-real-v1/`
- `05_validation/evidence/artifacts/d4c-rotation-kernel-v1/`
