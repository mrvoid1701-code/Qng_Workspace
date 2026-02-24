# QNG Core Derivation — Discrete-to-Continuum Bridge v1

- Scope: Fundamental derivations (TASKS.md P8 / line 103)
- Date: 2026-02-22
- Authored by: Claude Sonnet 4.6
- Related claims: QNG-C-093, QNG-C-094, QNG-C-029, QNG-C-032
- Inputs:
  - `03_math/derivations/qng-core-emergent-metric-v1.md`
  - `03_math/derivations/qng-core-gr-bridge-v1.md`
  - `01_notes/core-closure-v1.md`
- Status: formalized (foundational assumptions locked)

---

## Objective

Define the explicit passage from the discrete QNG node graph to continuum field equations, identifying which assumptions are made at each step and what breaks down at each scale.

---

## 1) Discrete Setup

The QNG state at time `t` is a graph:

```
G(t) = (N(t), E(t))
```

where each node `i ∈ N(t)` carries:

```
N_i(t) = (V_i(t), chi_i(t), phi_i(t))
Sigma_i(t) ∈ [0, 1]
```

The discrete Sigma field is defined at nodes. Edges encode local adjacency (spatial proximity in the target continuum).

---

## 2) Coarse-Graining Assumption (A1)

**Assumption A1:** There exists a coarse-graining length scale `L_CG >> l_node` such that, when averaging over a ball of radius `L_CG`, the discrete node distribution becomes approximately continuous.

Formally, define a smoothed field:

```
Sigma_s(x) = sum_i Sigma_i * K((x - x_i) / L_CG) / Z(x)
```

where `K` is a smoothing kernel (Gaussian in v3) and `Z(x)` is a normalization factor.

**This is the single most load-bearing assumption in the theory.** If the node distribution is fractal or highly inhomogeneous at all scales, A1 fails and the continuum limit does not exist.

**Status:** Not derived — postulated. Testable only indirectly via metric stability gates (D2 coarse-grain stability).

---

## 3) Continuum Sigma Field

Under A1, `Sigma_s(x)` is a smooth scalar field on a 2D (or 3D) manifold `M`.

Gradient and Hessian are well-defined:

```
(nabla Sigma_s)^i = g^{ij} partial_j Sigma_s
Hess(Sigma_s)_ij = partial_i partial_j Sigma_s - Gamma^k_{ij} partial_k Sigma_s
```

In the flat (Euclidean chart, weak-field regime):

```
Hess(Sigma_s)_ij ≈ partial_i partial_j Sigma_s
```

---

## 4) Emergent Metric (A2)

**Assumption A2:** The effective spatial metric is identified with the negative Hessian of the smoothed Sigma field, after SPD projection and conformal normalization:

```
g_ij(x) = normalize(SPD_proj(-Hess(Sigma_s)_ij))
```

with unit-trace conformal gauge and fixed anisotropy shrinkage `k = 0.4`.

**This is a definitional choice, not a derivation from first principles.** Alternative metric definitions (e.g., from chi gradient, from node density) would produce different geometric structures.

**Status:** Locked in metric-lock-v3. Tested via D1-D4 gates. Pipeline-level stable.

---

## 5) Continuum Equations of Motion

Under A1 and A2, the QNG acceleration at position `x` is:

```
a_QNG(x) = -g^{ij}(x) partial_j Sigma_s(x)
```

In the flat weak-field limit (`g_ij ≈ g0_ij + h_ij`, `||h||_F << 1`):

```
a_QNG(x) ≈ -g0^{ij} partial_j Sigma_s + h^{ij} partial_j Sigma_s + O(h^2)
```

The first term is the Newtonian-like gradient flow. The second term encodes metric corrections from the memory field structure.

---

## 6) Memory Lag Term (A3)

**Assumption A3:** There is a causal memory lag in the update of `Sigma_s`. The full dynamical equation for a particle at position `x(t)` is:

```
a_total(x, t) = a_GR(x, t) + a_lag(x, t)
```

where:

```
a_lag(x, t) = -tau(x) * (v · nabla) nabla Sigma_s(x, t)
tau(x) = alpha_tau * chi(x)
chi(x) = coarse-grained node load at x
```

**This introduces two new free parameters:** `alpha_tau` (global coupling) and the kernel shape for how `chi` distributes over space. In v1, chi is linked to mass via `chi = m/c`.

**Status:** tau universality tested (T-F02 PASS, classic subset). Mass-chi coupling tested (STRATON-002 FAIL).

---

## 7) QM Limit (Sketch — Not Formalized)

The discrete node graph `G(t)` can in principle be mapped to a quantum amplitude structure if:

1. Node states carry complex amplitudes: `N_i(t) → |psi_i(t)⟩`
2. The update operator `U` is unitary.
3. Measurement corresponds to projection onto eigenstates of `Sigma`.

This mapping is **not formalized in v1**. The QM limit is speculative and not required for the trajectory/lensing/timing predictions.

**Status:** open (TASKS.md line 103 — derivazioni fundamentale GR/QM partially addressed here; QM sector remains open).

---

## 8) Breakdown Scales

| Scale | What breaks | Consequence |
|---|---|---|
| `l < l_node` | Coarse-graining A1 fails | Metric undefined; discrete effects dominate |
| `L_CG` not >> `l_node` | Smooth Sigma field unreliable | Metric gates may fail (D2 coarse-grain drift) |
| `||h||_F ~ 1` | Weak-field expansion breaks | Full nonlinear metric needed |
| `tau > t_dynamical` | Memory lag exceeds system timescale | Lag term dominates over GR; unphysical regime |

---

## 9) Assumptions Summary

| ID | Assumption | Type | Testable? | Current status |
|---|---|---|---|---|
| A1 | Coarse-graining limit exists at `L_CG` | Postulate | Indirectly (D2) | Passes D2 on pipeline |
| A2 | Metric = normalized SPD(-Hessian(Sigma)) | Definition | Yes (D1-D4) | Pass (3 datasets) |
| A3 | Memory lag with universal tau | Postulate | Yes (T-F02, STRATON) | Partial (tau universal in trajectory; mass coupling FAIL) |
| A4 | chi = m/c (mass-load mapping) | Ansatz | Yes (STRATON series) | FAIL (STRATON-002) |
| A5 | QM unitary limit | Sketch | Not yet | Open |
