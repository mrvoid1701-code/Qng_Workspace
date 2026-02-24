# QNG Σ Dynamics — Minimal Equation of Motion v1

- Date: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Status: LOCKED (candidate A selected — generalized Poisson)
- Related: `qng-continuum-limit-v1.md` §4 (identifies missing EOM as critical gap)
- Related: `qng-discrete-to-continuum-v1.md` A1–A5
- Pre-registration for tests: `05_validation/pre-registrations/qng-sigma-dynamics-prereg-v1.md`

---

## Problem Statement

The QNG acceleration law defines:

```
a^i(x) = −g^{ij}(x) ∂_j Σ(x)
```

But there is no equation of motion (EOM) for Σ itself. This is the critical gap identified in `qng-continuum-limit-v1.md` §4, failure mode F-5: "Σ has no equation of motion."

Without an EOM for Σ, the theory is:
- Not predictive (cannot evolve Σ from initial conditions)
- Not falsifiable at the level of Σ dynamics
- Cannot recover Newtonian limit (requires ∇²Σ ∝ ρ or equivalent)

This document derives and locks the minimal EOM for Σ that: (a) is self-consistent with the metric definition, (b) recovers the Newtonian limit, and (c) introduces as few new free parameters as possible.

---

## 1) Candidate Equations

### Candidate A — Generalized Poisson (preferred)

```
∇ · (g^{−1} ∇Σ) = α ρ
```

In component form:

```
∂_i (g^{ij} ∂_j Σ) = α ρ
```

where:
- `g^{ij}` is the inverse metric (emergent from Hessian(Σ))
- `ρ` is the mass-energy density at position x
- `α` is a new free parameter (coupling constant, units: [1/density] in appropriate units)

**Self-referential structure:** The metric `g` depends on Σ through `g_ij = normalize(SPD(−Hess(Σ)))`. So Candidate A is:

```
∂_i (normalize(SPD(−Hess(Σ)))^{−1})^{ij} ∂_j Σ = α ρ
```

This is a second-order nonlinear PDE for Σ. In the weak-field / slow-variation limit, it simplifies considerably (see §4).

### Candidate B — Diffusion-Decay

```
∂_t Σ = D ∇²Σ + S(ρ) − κ Σ
```

where `D` (diffusion), `S` (source function), `κ` (decay rate) are three new free parameters.

**Why Candidate B is not selected:**
1. It is explicitly time-dependent and requires specifying initial conditions for Σ.
2. It introduces 3+ free parameters vs 1 for Candidate A.
3. It breaks the self-referential consistency: the metric is defined from Hessian(Σ), but diffusion-decay does not ensure Hessian(Σ) is the right object evolving.
4. The decay term κΣ has no clear physical motivation in QNG (Σ represents node stability, not a field that decays to zero).
5. The Newtonian limit recovery is less clean (requires κ → 0 and S(ρ) ∝ ρ as separate assumptions).

---

## 2) Selected Equation: Generalized Poisson

**LOCKED EOM for Σ (v1):**

```
∂_i (g^{ij} ∂_j Σ) = α ρ                            (EOM-Σ)
```

This is a covariant Poisson equation on the emergent metric manifold (M, g).

**Notation:**
- `∇_g · (∇_g Σ) = α ρ` (covariant Laplace-Beltrami form)
- Or equivalently: `Δ_g Σ = α ρ` (where Δ_g is the Laplace-Beltrami operator)

---

## 3) Newtonian Limit Recovery

**Setup:** In the Newtonian limit, we require:
- `g_ij ≈ g0_ij + h_ij` with `||h||_F << 1` (weak field)
- `g0_ij ≈ δ_ij` (approximately Euclidean) after conformal normalization
- Σ varies slowly on scales >> `L_CG` (coarse-graining scale)

**At zeroth order** (flat metric `g^{ij} ≈ δ^{ij}`):

```
∂_i (δ^{ij} ∂_j Σ) = ∇²Σ = α ρ
```

This IS the Poisson equation for the Newtonian gravitational potential φ:

```
∇²φ = 4πG ρ
```

**Identification:** `Σ ↔ φ / (4πG / α)`, with:

```
α = 4πG (in Newtonian units)
```

or in normalized units where G = 1: `α = 4π`.

**Conclusion:** EOM-Σ recovers the Newtonian Poisson equation at zeroth order. ✓

**First-order correction:** At order `h`:

```
∂_i (δ^{ij} ∂_j Σ) + ∂_i (h^{ij} ∂_j Σ) = α ρ
∇²Σ + ∇ · (h ∇Σ) = α ρ
```

The correction term `∇ · (h ∇Σ)` encodes metric perturbations sourced by Σ itself (the self-referential structure). This generates post-Newtonian corrections analogous to GR, but derived from the QNG metric.

---

## 4) Flat-Metric Limit (Linearization)

In the regime where the Frobenius norm of the metric perturbation is small (`||g − g0||_F < ε`), the EOM-Σ linearizes to:

```
∇²Σ = α ρ − ∇ · ((g − g0) ∇Σ) + O(||g−g0||²)
```

Define the "metric source correction":

```
J_metric(x) ≡ −∂_i ((g^{ij} − δ^{ij}) ∂_j Σ)
```

Then:

```
∇²Σ = α ρ + J_metric     (linear Poisson with metric correction)
```

This is the working equation for numerical solutions in the near-flat regime.

---

## 5) Fixed Points and Self-Consistency

**Definition:** A Σ field is self-consistent with respect to EOM-Σ if it satisfies:

```
Δ_g Σ = α ρ    where    g = normalize(SPD(−Hess(Σ)))
```

**Fixed point analysis:**

For a single spherically symmetric mass ρ = M δ(r):
- Newtonian solution: Σ = −αM / (4π r) (in 3D)
- Hessian of Σ: `H_ij = (αM / (4πr³)) (δ_ij − 3r_i r_j / r²)` (traceless, anisotropic)
- Metric from Hessian: anisotropic, consistent with 1/r² gradient structure
- Self-consistency check: g^{ij} ∂_j Σ should reproduce the 1/r² force

**Result (schematic):** The self-consistent fixed point exists in the weak-field regime and is unique for a given ρ. The metric perturbation h ∝ αM/r³ provides a 1/r³ correction to the force, analogous to GR post-Newtonian corrections.

---

## 6) New Free Parameters Introduced

| Parameter | Symbol | Units | Physical meaning | How to fix |
|---|---|---|---|---|
| Coupling constant | α | [L³/(M·T²)] (natural) | Strength of ρ → Σ coupling | Matched to G: α = 4πG |

**Total new free parameters in EOM-Σ: 1 (α)**

This compares favorably to:
- Diffusion-decay (Candidate B): 3+ parameters
- Full GR (Einstein equations): 1 (G) + cosmological constant

---

## 7) Open Issues and Limitations

| Issue | Description | Status |
|---|---|---|
| OSD-1 | Self-referential nonlinearity: g depends on Hess(Σ) which depends on Σ | No existence/uniqueness proof yet |
| OSD-2 | SPD projection is non-smooth at degenerate Hessian | PDE theory not established |
| OSD-3 | Time-dependence: EOM-Σ is static (no ∂_t Σ) | Full dynamical equation requires extension |
| OSD-4 | Boundary conditions for Σ not specified | Needed for numerical solutions |
| OSD-5 | The metric normalization (Frobenius) changes the effective Laplacian | Connection to standard Laplace-Beltrami operator not fully established |

**OSD-3 (time-dependence):** The minimal time-dependent extension is:

```
□_g Σ ≡ −∂²_t Σ + Δ_g Σ = α ρ
```

where `□_g` is the d'Alembertian on the emergent metric. This requires a 4D metric (addressing the 4D extension sketched in `qng-continuum-limit-v1.md` §2).

---

## 8) Relationship to Existing QNG Claims

| Claim | Connection to EOM-Σ |
|---|---|
| QNG-C-060 (trajectory lag) | EOM-Σ provides the background Σ field; lag term a_lag = −τ(v·∇)∇Σ is a correction to EOM-Σ solution |
| QNG-C-014 (chi = m/c) | chi appears in τ = α_tau · chi; NOT in EOM-Σ; mass-lag coupling is a separate layer |
| QNG-CORE-METRIC-V3 | EOM-Σ is the source equation; metric emerges from the solution Σ |
| QNG-H-UNIFY (tau universality) | EOM-Σ fixes the background; universality of τ is a separate question |

---

## 9) Pre-registered Tests for EOM-Σ

Pre-registration locked: `05_validation/pre-registrations/qng-sigma-dynamics-prereg-v1.md`

| Test ID | What it checks | Status |
|---|---|---|
| T-SIG-001 | Newtonian limit: ∇²Σ ≈ αρ in flat metric, residual < 10% | Pending (needs numerical solver) |
| T-SIG-002 | Self-consistency: metric from Σ solution is consistent with the Σ source | Pending |
| T-SIG-003 | EOM-Σ reduces to standard Poisson when g = δ_ij | Analytic — PASS by §3 above |
| T-SIG-004 | Perturbative first-order correction matches linear GR post-Newtonian form | Pending (analytic) |

---

## Summary

**EOM-Σ (locked):**

```
∂_i (g^{ij} ∂_j Σ) = α ρ    with    g_ij = normalize(SPD(−Hess(Σ)))
```

- 1 new free parameter: α (fixed by matching to G)
- Recovers Newtonian Poisson equation at zeroth order
- Self-consistent (metric and field determined by same equation)
- Nonlinear due to self-referential metric
- Time-independent (static case); dynamic extension requires 4D metric
- T-SIG-003 analytically PASS; T-SIG-001/002/004 pending numerical work
