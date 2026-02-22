# Pre-Registration - QNG-T-GEODESIC-001

- Date: 2026-02-21
- Test ID: `QNG-T-GEODESIC-001`
- Scope: metric-v3 trajectory/geodesic sanity across locked synthetic datasets

## Fixed Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_geodesic_001.py `
  --test-id QNG-T-GEODESIC-001 `
  --dataset-ids DS-002,DS-003,DS-006 `
  --samples 72 `
  --seed 3401 `
  --steps 40 `
  --dt 0.05 `
  --out-dir 05_validation/evidence/artifacts/qng-t-geodesic-001
```

## Gates (Locked)

- `G1 stability`: stable trajectory fraction `>= 0.99` on each dataset.
- `G2 Newtonian direction`: metric-vs-Newton direction cosine median `>= 0.95` and p10 `>= 0.90` on each dataset.
- `G3 magnitude sanity`: acceleration magnitude ratio median in `[0.50, 3.00]` and p90 `<= 3.50` on each dataset.

## Final Decision

- Pass only if all `G1..G3` pass on all listed datasets.

## Stop Conditions

- Any threshold change requires `qng-t-geodesic-001-v2.md`.

