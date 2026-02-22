# QNG Core Derivation - Emergent Continuous Metric (v1)

- Scope: fundamental closure task (P8)
- Date: 2026-02-21
- Related claims: `QNG-C-018`, `QNG-C-019`, `QNG-C-100`, `QNG-C-093`
- Lock references:
  - `01_notes/metric/metric-lock-v1.md`
  - `05_validation/pre-registrations/qng-metric-hardening-v1.md`
- Status: formalized

## Objective

Show that a continuous effective metric can be inferred from a coarse-grained graph distance and audited with fixed gates.

## 1) Nodes + Connections

Discrete substrate:

```text
G_t = (N_t, E_t)
N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))
```

No background metric is assumed.

## 2) Topological Distance

Weighted geodesic distance:

```text
D_graph(u,v) = min_{gamma:u->v} sum_{e in gamma} w_e
```

with `w_e > 0` and numeric normalization by median edge length.

## 3) Coarse-Graining

Distance smoothing (Gaussian kernel at scale `s`):

```text
D_s(p,i) = [sum_j exp(-D_graph(i,j)^2/(2 s^2)) D_graph(p,j)] / [sum_j exp(-D_graph(i,j)^2/(2 s^2))]
```

locked scales: `{s0, 1.25 s0, 1.5 s0}`.

## 4) Continuous Limit

Assume local chart coordinates `delta` exist from distance-only embedding around each anchor `p`:

```text
delta = (delta^1, delta^2)
```

Metricizability condition:

```text
D_s(p,p+delta)^2 = g_ij(p) delta^i delta^j + O(|delta|^3)
```

## 5) Emergent Metric

BOXED 1 - local scalar function:

```text
F_p(delta) = (1/2) D_s^2(p, p+delta)
```

BOXED 2 - metric definition:

```text
g_ij(p) = [partial^2 F_p / (partial delta^i partial delta^j)]_{delta=0}
```

BOXED 3 - discrete estimator (local quadratic regression):

```text
F_p(delta_k) ~= c + b_i delta_k^i + (1/2) g_11 (delta_k^1)^2 + g_12 delta_k^1 delta_k^2 + (1/2) g_22 (delta_k^2)^2
```

Estimate coefficients by ridge least squares on neighborhood samples `{delta_k}`.

Equivalent finite-difference form (for symmetric local stencils):

```text
g_ii ~= [F_p(+h e_i) - 2 F_p(0) + F_p(-h e_i)] / h^2
g_ij ~= [F_p(h e_i + h e_j) - F_p(h e_i - h e_j) - F_p(-h e_i + h e_j) + F_p(-h e_i - h e_j)] / (4 h^2)
```

## Step Size / delta Selection

- `delta_k` are local chart coordinates from two-landmark geodesic tangent chart.
- Stability band for usable points:
  - `|delta_k| in [h_min, h_max]`, with `h_min = 0.5*s0`, `h_max = 2.0*s0`.
- Points outside this band are excluded from local metric fit to avoid singular or high-curvature bias.

## Compatibility with Sigma

Given local Sigma gradient:

```text
partial_j Sigma
```

define metric-based acceleration direction:

```text
a^i_metric = -g^{ij} partial_j Sigma
```

and compare with raw direction `-nabla Sigma` by cosine similarity gates.

## Minimal Credibility Conditions

1. SPD/signature gate:
   - `min eig(g(p)) >= eps` (space metric).
2. Coarse-grain stability:
   - `Delta_g(s) = ||g(s)-g(s0)||_F / ||g(s0)||_F` remains bounded by prereg thresholds.
3. Sigma compatibility:
   - median and tail cosine gates pass.
4. Negative control:
   - shuffled Sigma labels collapse compatibility.

## Falsifier

Emergent-metric claim is falsified if any persists under locked v1 setup:

- non-SPD metric in stable neighborhoods,
- unstable `g` under scale change,
- no alignment between `a_metric` and `-nabla Sigma`,
- shuffled-Sigma control does not collapse D3 metric.

## Output Class

Pipeline-level formalization with executable gates (not alone a REAL-data confirmation).

