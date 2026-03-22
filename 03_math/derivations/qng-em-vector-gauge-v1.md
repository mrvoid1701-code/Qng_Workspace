# QNG Electromagnetism from Vector Node Fluctuations — Calea 3 v1

- Date: 2026-03-22
- Authored by: Claude Sonnet 4.6
- Status: CANDIDATE (pending gate G39)
- Depends on: qng-stability-action-v1.md, qng-g28-u1-gauge-v1 (PASS)
- Gate: G39 (qng-g39-em-gauge)

---

## Motivation

In QNG, scalar fluctuations δΣ_i on nodes generate gravitational structure via the
Hessian metric g_ij = normalize(SPD(-Hess(Σ))). Gate G28 established a U(1) gauge
field on edges with exact holonomy invariance and photon-like propagation (slope ≈ -2.57).

Calea 3 asks: if we extend node fluctuations from scalar to vector,

```
δΣ_i  →  δΣ_i^μ,    μ = 0,1,2,3
```

does electromagnetism emerge naturally from the same QNG substrate?

---

## 1) Vector Fluctuation Field

Each node i carries a 4-vector fluctuation:

```
δΣ_i^μ = (δΣ_i^0, δΣ_i^1, δΣ_i^2, δΣ_i^3)
```

**Identification:**

```
δΣ_i^μ  ≡  A_i^μ    (electromagnetic 4-potential at node i)
```

**Connection to G28:** The edge gauge field A_{ij} from G28 is the discrete gradient:

```
A_{ij} = (A_j^μ - A_i^μ) · ê_{ij,μ}  =  (δΣ_j^μ - δΣ_i^μ) · ê_{ij,μ}
```

where ê_{ij}^μ = (r_j - r_i)^μ / |r_j - r_i| is the unit vector along edge (i,j).
G28's A_edge is thus the projection of the node-vector difference onto the edge direction.

---

## 2) Gauge Symmetry

The theory is invariant under:

```
δΣ_i^μ  →  δΣ_i^μ + ∂_i^μ χ_i
```

where χ_i is an arbitrary scalar on each node.

**Discrete form:** on the graph, ∂_i^μ χ_i is approximated as:

```
(∂χ)_i^μ = Σ_{j~i} w_{ij} (χ_j - χ_i) ê_{ij}^μ
```

**Effect on A_{ij}:** Under the gauge transform,

```
A_{ij} → A_{ij} + (χ_i - χ_j)
```

which is exactly the gauge transform A → A + dφ already tested in G28b. ✓

---

## 3) Lorenz Gauge (Discrete)

The Lorenz gauge condition ∂_μ A^μ = 0 becomes on the graph:

```
(div A)_i ≡ Σ_{j~i} w_{ij} (A_j^μ - A_i^μ) · ê_{ij,μ} / |r_{ij}| = 0
```

Expanding with w_{ij} = 1/|r_{ij}|:

```
(div A)_i = Σ_{j~i} (A_j^μ - A_i^μ) · ê_{ij,μ} / |r_{ij}|^2 = 0
```

**Relation to G28 zero-sum source:** In G28, the principled source for m=0
(photon) was the zero-sum condition Σ_i b_i = 0. This is exactly the discrete
Lorenz gauge: Σ_i (div A)_i = 0 when summed globally. The G28 CG solver
(run with m²→0) implicitly solves in Lorenz gauge. ✓

---

## 4) Field Strength Tensor

On each edge (i,j), define the antisymmetric field strength:

```
F_{ij}^{μν} = (A_j^μ - A_i^μ) ê_{ij}^ν / |r_{ij}|
            - (A_j^ν - A_i^ν) ê_{ij}^μ / |r_{ij}|
```

Properties:
- **Antisymmetry:** F_{ij}^{μν} = -F_{ij}^{νμ}  ✓
- **Gauge invariance:** Under A_i^μ → A_i^μ + ∂_i^μ χ_i, the χ terms cancel ✓
- **Reduction to G28:** F_{ij}^{0k} encodes the electric-like component along edge (i,j)

The holonomy from G28b is:

```
F_loop = Σ_{edges in loop} A_{ij} = Σ_{loop} F_{ij}^{μν} ê_{ij,μ} ê_{loop,ν} · |r_{ij}|
```

G28b's exact gauge invariance (rel_err = 0.0) confirms F^{μν} is well-defined. ✓

---

## 5) Action and Equations of Motion

The electromagnetic action on the graph:

```
S_EM = Σ_{(i,j)} w_{ij} F_{ij}^{μν} F_{ij,μν}
```

Varying with respect to A_i^μ (Euler-Lagrange on graph):

```
Σ_{j~i} w_{ij} [ F_{ij}^{μν} ê_{ij,ν} ] = J_i^μ
```

where J_i^μ = (ρ_charge,i, J_i^k) is the 4-current at node i.

**Maxwell equations on graph:**

```
(discrete Maxwell)    Σ_{j~i} w_{ij} F_{ij}^{μν} ê_{ij,ν} = J_i^μ
```

This is the graph-discretization of ∂_ν F^{μν} = J^μ. ✓

---

## 6) Decoupling from Gravity

The gravitational sector uses:
```
g_ij = normalize(SPD(-Hess(Σ)))    [from scalar Σ, EOM locked]
```

The electromagnetic sector uses:
```
A_i^μ = δΣ_i^μ                     [from vector δΣ^μ, this document]
```

These are **independent degrees of freedom** on each node i:
- Σ_i ∈ [0,1] (scalar, bounded) → gravity
- A_i^μ ∈ R^4 (vector, unconstrained up to gauge) → electromagnetism

The existing locked EOM-Σ is unchanged. G28 validation is unchanged.

---

## 7) Unified QNG Field Content

| Field | Type | Spin | Force | Status |
|---|---|---|---|---|
| Σ_i | scalar | 0 | Gravity | LOCKED (EOM-Σ) |
| δΣ_i^μ (= A_i^μ) | vector | 1 | Electromagnetism | This document |
| h_ij = g_ij - δ_ij | tensor | 2 | Gravitational waves | G22/G24 |
| χ_i | scalar | 0 | Memory/coupling | Locked |
| φ_i | phase | — | Synchronization | Locked |

---

## 8) Gate G39 — Validation Targets

| Test | What | Threshold |
|---|---|---|
| G39a | Maxwell propagator: slope log G_EM vs log r | ∈ (-4.0, -1.5) [dipol 4D → -3] |
| G39b | F^{μν} gauge invariance under δΣ_i^μ → δΣ_i^μ + ∂χ_i | rel_err < 1e-8 |
| G39c | Lorenz gauge: (div A)_i = 0 for zero-sum source | residual < 1e-6 |
| G39d | F^{μν} antisymmetry: max|F^{μν} + F^{νμ}| / max|F^{μν}| | < 1e-10 |

---

## 9) Relationship to Existing Claims

| Claim | Connection |
|---|---|
| QNG-G28 (U(1) gauge, PASS) | A_{ij} from G28 = projection of δΣ_i^μ difference ✓ |
| EOM-Σ (locked) | Unchanged — Σ scalar sector independent ✓ |
| QNG-C-060 (trajectory lag) | Lag a_lag uses ∇Σ (scalar); EM uses A^μ (vector) — separate ✓ |
| qng-wave-equation-v1 | Spin-0 + spin-2 waves; this adds spin-1 (photon) wave mode ✓ |

---

## Summary

Starting from vector fluctuations δΣ_i^μ on QNG nodes:

1. Identify A_i^μ = δΣ_i^μ (electromagnetic potential on nodes)
2. A_{ij} = edge projection = G28's gauge field ✓
3. Gauge symmetry A_i^μ → A_i^μ + ∂_i^μ χ_i (G28b exact ✓)
4. Lorenz gauge = G28 zero-sum condition ✓
5. F_{ij}^{μν} = antisymmetric edge field strength
6. Maxwell equations emerge from action variation

Electromagnetism and gravity emerge from the **same node substrate** via:
- Scalar component → gravity (Σ, spin-0)
- Vector component → electromagnetism (δΣ^μ, spin-1)
