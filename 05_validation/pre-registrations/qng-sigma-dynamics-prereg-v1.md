# QNG Σ Dynamics — Pre-registration v1

- Date locked: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Status: LOCKED
- Equation locked: `03_math/derivations/qng-sigma-dynamics-v1.md`
- EOM: `∂_i (g^{ij} ∂_j Σ) = α ρ`  with  `g = normalize(SPD(−Hess(Σ)))`

---

## Purpose

Lock the pre-registered tests for the Σ dynamics equation (EOM-Σ) before any numerical implementation.

---

## Locked Equation

```
Δ_g Σ = α ρ
```

where `Δ_g` is the Laplace-Beltrami operator on the emergent metric (M, g). This is the unique minimal EOM that:
1. Recovers Newtonian Poisson equation at zeroth order (g ≈ δ)
2. Has exactly one new free parameter (α)
3. Is self-consistent with the metric definition g = normalize(SPD(−Hess(Σ)))

---

## Pre-registered Tests

### T-SIG-001 — Newtonian Limit Test

**Claim:** In the flat metric limit (`||g − δ||_F < 0.01`), the solution Σ to EOM-Σ satisfies:

```
|∇²Σ − α ρ| / (α ρ_max) < 0.10
```

at 90% of grid points.

**Method:**
1. Solve EOM-Σ on a 2D grid (100×100) with point mass ρ = M δ(r) at origin.
2. Initialize g = δ (flat start).
3. Iterate: update Σ via standard Poisson solver; update g from Hess(Σ); repeat until |ΔΣ| < tol.
4. Measure residual `|∇²Σ − αρ|` relative to αρ_max.

**Gate:** 90th percentile of residual < 0.10. Expected: PASS (Newtonian recovery guaranteed by §3 of derivation).

**Status:** Pending numerical implementation.

### T-SIG-002 — Self-Consistency Convergence Test

**Claim:** The fixed-point iteration `g_{n+1} = normalize(SPD(−Hess(Σ_n)))` converges, where `Σ_n` solves `∂_i (g_n^{ij} ∂_j Σ_n) = αρ`.

**Method:**
1. Start with g_0 = δ (flat).
2. At each step: solve Poisson with current metric, update metric.
3. Measure convergence: `||g_{n+1} − g_n||_F / ||g_n||_F`.

**Gate:** Convergence criterion `||g_{n+1} − g_n||_F / ||g_n||_F < 0.01` achieved within 50 iterations, for at least one mass configuration.

**Status:** Pending numerical implementation.

### T-SIG-003 — Analytic Flat-Metric Limit (PASS by construction)

**Claim:** When g = δ_ij, EOM-Σ reduces to `∇²Σ = αρ`.

**Proof:** Substituting g^{ij} = δ^{ij} into `∂_i (g^{ij} ∂_j Σ) = αρ` gives `∂_i ∂_i Σ = ∇²Σ = αρ`. ∎

**Gate:** Analytic proof complete. **STATUS: PASS**

### T-SIG-004 — Post-Newtonian Structure Test (analytic, pending)

**Claim:** The first-order metric correction to EOM-Σ generates a force correction of the form:

```
δa^i = −h^{ij} ∂_j Σ
```

where `h_ij = g_ij − δ_ij`. This should match the linearized GR post-Newtonian acceleration to leading order.

**Method:** Expand EOM-Σ to first order in h; derive force correction; compare with linearized GR.

**Gate:** The force correction from EOM-Σ is proportional to `h ∇Σ`, consistent with metric-gravity coupling (not a quantitative match to GR required — just the functional form).

**Status:** Pending analytic completion.

---

## Anti-Gaming Policy

1. The EOM (`Δ_g Σ = αρ`) is locked and cannot be changed based on T-SIG-001/002 outcomes.
2. If T-SIG-001 fails (residual > 0.10), this is reported as a failure of Newtonian limit recovery, not corrected by threshold relaxation.
3. If T-SIG-002 fails (no convergence), this is reported as a self-consistency failure, not resolved by changing the iteration scheme post-hoc.
4. The free parameter α is locked to `α = 4πG` for T-SIG-001/002. If this fails, a fit of α is allowed as a separate track (α_fit), clearly labeled as post-hoc calibration.

---

## Open Questions Not Addressed (deferred to v2)

| Question | Why deferred |
|---|---|
| Dynamic EOM (∂_t Σ term) | Requires 4D metric — separate derivation |
| Boundary conditions for Σ | Domain-specific; handled in numerical tests |
| Uniqueness of self-consistent solution | Requires full PDE analysis |
| Time-dependence of ρ (moving sources) | Memory lag term is already a separate module |

---

## Summary Table

| Test | Type | Gate | Status |
|---|---|---|---|
| T-SIG-001 | Numerical | 90th-pct residual < 0.10 | Pending |
| T-SIG-002 | Numerical | Convergence < 0.01 in ≤50 iter | Pending |
| T-SIG-003 | Analytic | g=δ → ∇²Σ=αρ (proof) | PASS |
| T-SIG-004 | Analytic | Force correction ∝ h∇Σ | Pending |
