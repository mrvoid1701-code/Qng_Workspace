# Metric Lock v1

Date: 2026-02-21  
Scope: lock all definitions for emergent-metric hardening (`QNG-T-METRIC-001`).

## 1) Graph Distance

- Base graph: `G=(N,E)` from dataset-specific generator/ingest.
- Edge weights:
  - weighted shortest path with positive weights `w_e > 0`.
  - runner v1 uses normalized weights:
    - `w_e_norm = w_e_raw / median_edge_length_raw`.
- Graph distance:
  - `D_graph(u,v) = min_{paths u->v} sum_e w_e_norm`.

## 2) Coarse-Grain Distance

- Smoothed distance from anchor neighborhood uses Gaussian kernel on local graph distances:

```text
D_s(p,i) = [sum_j exp(-D_graph(i,j)^2 / (2 s^2)) * D_graph(p,j)] / [sum_j exp(-D_graph(i,j)^2 / (2 s^2))]
```

- Scale lock:
  - `s0 = 1.0` (post-normalization unit).
  - test scales: `{s0, 1.25*s0, 1.5*s0}`.

## 3) Local Chart / Embedding

- Method lock: two-landmark geodesic tangent chart (distance-only local embedding).
- For each anchor `p`:
  - choose landmark `l1` = farthest local point by `D_graph(p, .)`,
  - choose landmark `l2` maximizing non-collinearity (largest geodesic triangle height),
  - reconstruct local coordinates `delta=(x,y)` by distance-triangulation in this chart.

## 4) Sampling

- Anchor sampling strategy (locked):
  - 50% top-`Sigma` anchors (high-stability region),
  - 50% stratified random across `Sigma` quantile bins.
- Local neighborhood size:
  - fixed `m=20` nodes per anchor (including anchor).

## 5) Numeric Normalization

- All geodesic distances divided by median edge length before metric estimation.
- This sets stable scale and avoids blow-up in Hessian estimation.

## 6) Change-Control Rule

- This lock is immutable for v1.
- Any change to:
  - distance definition,
  - smoothing kernel,
  - chart method,
  - scales,
  - sampling policy,
  - normalization
  requires new file `metric-lock-v2.md` and new prereg entry.

