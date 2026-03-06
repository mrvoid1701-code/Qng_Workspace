# D4 Stage-2 Forensics v1

- generated_utc: `2026-03-06T01:22:53.913969+00:00`
- summary_json: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-dual-kernel-v2-strict-vs-mond/d4_stage2_dual_kernel_summary.json`
- dataset_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/data/rotation/rotation_ds006_rotmod.csv`
- split_seed/train_frac: `3401/0.7`
- best_dual_params: `tau=0.5, alpha=0.3, k1=0.16345889166689903, k2=0.0`

## Holdout Loss Signature

- holdout points: `1070`
- mean chi2 gap per point (dual - mond): `194.949686`
- p50/p90 chi2 gap: `10.386900/287.428805`

## Top Holdout Failing Segments (by chi2_gap_per_n)

- `split_accel` (accel=low_accel): gap_per_n=458.174612, dual_per_n=487.716642, mond_per_n=29.542030, n=386
- `split_radius` (radius=mid): gap_per_n=341.443832, dual_per_n=388.867386, mond_per_n=47.423554, n=320
- `split_galaxy_class` (class=high_mass_proxy): gap_per_n=299.476852, dual_per_n=369.208450, mond_per_n=69.731598, n=491
- `split_radius` (radius=outer): gap_per_n=269.853831, dual_per_n=288.329539, mond_per_n=18.475708, n=297
- `split_galaxy_class` (class=low_mass_proxy): gap_per_n=117.771848, dual_per_n=139.524367, mond_per_n=21.752519, n=286

## Hypothesized Mechanisms (data-driven)

1. High gap concentration in low-acceleration holdout regime suggests missing long-range support beyond current kernel fit.
2. Outer-radius penalties indicate underestimation at large r even when null is improved.
3. System-level concentration (worst_galaxies.csv) indicates morphology-dependent miss not captured by current global parameterization.
