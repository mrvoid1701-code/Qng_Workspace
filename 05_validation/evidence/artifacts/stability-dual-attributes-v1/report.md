# Stability Dual-Attributes Diagnostic (v1)

- generated_utc: `2026-03-03T14:41:51.805722+00:00`
- S1 definition: energetic channel (`gate_energy_drift` behavior).
- S2 definition: structural channel (all non-energy stability gates + core-support stability descriptors).

## Lane Summary

### stability-convergence-v4
- structural_profile_pass_fraction: `1.000000`
- energetic_profile_pass_fraction: `0.839259`
- structural_seed_pass_fraction: `1.000000`
- energetic_seed_pass_fraction: `0.000000`
- full_seed_pass_fraction: `0.900000`
- bulk_seed_pass_fraction: `0.150000`

### stability-convergence-v5
- structural_profile_pass_fraction: `1.000000`
- energetic_profile_pass_fraction: `0.842857`
- structural_seed_pass_fraction: `1.000000`
- energetic_seed_pass_fraction: `0.000000`
- full_seed_pass_fraction: `0.450000`
- bulk_seed_pass_fraction: `0.000000`

## Interpretation

- If S2 stays near 1.0 while S1 degrades, stability behaves as at least two separable attributes (energetic vs structural).
- This diagnostic is evidence-only and does not redefine official gates.
