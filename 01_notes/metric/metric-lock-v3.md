# Metric Lock v3

Date: 2026-02-21  
Scope: v3 method change for emergent metric hardening after v2 partial recovery (no gate retuning).

## 1) Graph Distance

- Base graph: `G=(N,E)` with positive edge weights.
- Distance:
  - `D_graph(u,v) = min_path sum_e w_e`.
- Numeric normalization:
  - divide all graph distances by median edge length.

## 2) Coarse-Grain Variable

- v3 keeps smoothing target on **Sigma field** (same as v2), not anchor-distance field.
- For local neighborhood around anchor `p`:

```text
Sigma_s(i) = [sum_j exp(-D_graph(i,j)^2/(2 s^2)) Sigma(j)] / [sum_j exp(-D_graph(i,j)^2/(2 s^2))]
```

- Scale lock:
  - `s0 = 1.0` (normalized units),
  - scales `{s0, 1.25*s0, 1.5*s0}`.

## 3) Local Chart / Embedding

- Method lock:
  - two-landmark geodesic tangent chart (`distance-only` local chart).
- Coordinates:
  - local `delta=(x,y)` from geodesic triangulation around each anchor.

## 4) Sampling

- Anchor policy:
  - 50% top-`Sigma`,
  - 50% stratified random by `Sigma` quantiles.
- Local neighborhood size:
  - fixed `m=20`.

## 5) Metric Estimator (v3 change)

- Estimate local quadratic Sigma model:

```text
Sigma(x,y) ~= c + b1 x + b2 y + 0.5 h11 x^2 + h12 xy + 0.5 h22 y^2
```

- Hessian `H = [[h11,h12],[h12,h22]]`.
- Dynamic metric proxy from acceleration Jacobian (`a=-grad Sigma`):

```text
g_raw <- SPD_projection(-H)
```

where SPD projection uses eigen-decomposition and absolute eigenvalue floor.

- v3 adds two fixed post-projection operators:
  - conformal gauge normalization:

```text
g_conf <- g_raw / trace(g_raw)
```

  - fixed anisotropy shrinkage (locked):

```text
g_v3 <- k * g_conf + (1-k) * (I/2),   k = 0.4
```

This keeps Hessian directional content but removes unstable conformal drift across coarse-grain scales.

## 6) D4 Control Interpretation (Locked)

- D4 uses shuffled Sigma labels to recompute `g_shuf` and `grad_shuf`.
- Control cosine compares shuffled metric-driven acceleration direction against original raw direction.
- Expected collapse means method discriminates structured signal from random relabeling.

## 7) Change-Control Rule

- v3 lock is immutable.
- Any further method change requires `metric-lock-v4.md` + new prereg.
