# DS-003 G15b Diagnosis (Seed Sweep)

Run scope:

- Dataset: `DS-003`
- Seeds: `3401..3410`
- `phi_scale = 0.08`
- Script: `scripts/run_qng_ppn_debug_v1.py`

Summary:

- `G15b-v1` pass rate: `3/10`
- `G15b-v2` pass rate: `10/10`
- `G15 final` pass rate (still keyed to v1): `3/10`

Interpretation:

- Under DS-003 multi-peak geometry, `G15b-v1` (radial shells from a primary peak) is unstable.
- `G15b-v2` (potential quantiles) is stable with unchanged threshold `> 2.0`.
- This supports treating `v2` as the recommended candidate while keeping `v1` as legacy until promotion criteria are met.
