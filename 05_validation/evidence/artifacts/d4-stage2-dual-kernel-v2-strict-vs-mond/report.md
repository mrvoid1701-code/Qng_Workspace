# D4 Stage-2 Dual-Kernel Report (d4-stage2-dual-kernel-v2-strict-vs-mond)

- generated_utc: `2026-03-06T01:15:02Z`
- dataset_id: `DS-006`
- train/holdout galaxies: `122/53`
- train/holdout points: `2321/1070`

## Best Dual Parameters

- tau_kpc: `0.500000`
- alpha: `0.300000`
- k1: `0.163458892`
- k2: `0.000000000`

## Holdout Metrics

- null chi2/N: `270.776399`
- mond chi2/N: `46.690217`
- dual chi2/N: `241.639903`
- improve_vs_null_pct: `10.760353`
- delta_chi2_dual_minus_mond: `208596.164177`

## Notes

- Fixed split and fixed grids (pre-registered anti post-hoc policy).
- Global parameters only (no per-galaxy tuning).
- Kernels use radius + baryon_term only.
