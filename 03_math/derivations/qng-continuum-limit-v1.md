# QNG — Continuum Limit Derivation v1

- Date: 2026-02-22
- Authored by: Claude Sonnet 4.6
- Inputs:
  - `03_math/derivations/qng-core-emergent-metric-v1.md`
  - `03_math/derivations/qng-core-gr-bridge-v1.md`
  - `03_math/derivations/qng-discrete-to-continuum-v1.md`
  - `01_notes/metric/metric-lock-v3.md`
- Status: research derivation — hypothesis analysis, not confirmed theory
- Disclaimer: this document treats QNG as a research hypothesis. Every step is annotated with what is assumed, what is derived, and what is speculation.

---

## Setup

Starting equation (locked, from GR bridge v1):

```
a^i = -g^{ij} ∂_j Σ
```

where the metric in v3 conformal gauge (2D, trace = 1) is:

```
g_ij = normalize( SPD_proj( -∂_i ∂_j Σ_s ) )
```

`Σ_s` is the smoothed stability scalar field (Gaussian coarse-graining at scale s).
Normalization: `tr(g) = 1` → `g0_ij = (1/2) δ_ij` in flat background.

---

## Part 1 — Reduction to Newtonian Potential

### 1.1 Weak-Field Expansion

Decompose:

```
g_ij = g0_ij + h_ij,    g0_ij = (1/2) δ_ij,    tr(h) = 0
```

Inverse to first order in h:

```
g^{ij} = 2 δ^{ij} - h^{ij} + O(h²)
```

Acceleration:

```
a^i = -(2 δ^{ij} - h^{ij} + O(h²)) ∂_j Σ
a^i = -2 ∂^i Σ + h^{ij} ∂_j Σ + O(h²)
```

**Zeroth order:** `a^i ≈ -2 ∂^i Σ`

This is Newtonian gradient flow if `Σ = φ_N / 2`, i.e. if the stability field is half the gravitational potential.

For Newtonian gravity: `∇²φ_N = 4πG ρ` → `∇²Σ = 2πG ρ`.

### 1.2 Critical Constraint from Conformal Gauge (ASSUMPTION FAILURE)

**This is the first structural problem.**

Conformal normalization imposes:

```
tr(g) = 1  →  tr(-Hess(Σ_s)) = tr(g) · tr(-Hess(Σ_s)) / tr(...)
```

More precisely, the unnormalized matrix is `M_ij = -∂_i ∂_j Σ_s`. After trace normalization:

```
g_ij = M_ij / tr(M) = (-∂_i ∂_j Σ_s) / (-∇² Σ_s)
```

For this to equal `g0_ij = (1/2) δ_ij` at zeroth order, we need:

```
-∂_i ∂_j Σ_s ≈ (1/2) (-∇² Σ_s) δ_ij
```

This holds only when the Hessian of Σ is isotropic (proportional to the identity) — i.e., when Σ is locally quadratic with equal curvature in all directions.

**Conclusion:** The Newtonian identification `Σ = φ_N/2` is only consistent if the gravitational field is locally isotropic. For anisotropic fields (e.g., near non-spherical mass distributions), the conformal normalization introduces a systematic correction that has no Newtonian analogue. This is a regime where QNG and Newtonian gravity depart.

### 1.3 Newtonian Limit: Conditions

The acceleration reduces to Newtonian gradient descent (`a ≈ -∇φ_N`) when ALL of the following hold:

| Condition | Mathematical form | Physical meaning |
|---|---|---|
| C1 | `‖h‖_F ≪ 1` | Metric perturbation is small |
| C2 | `Hess(Σ) ≈ (∇²Σ/2) δ_ij` | Isotropic local curvature |
| C3 | `∇²Σ = 2πGρ` (external input) | Σ satisfies sourced Poisson equation |
| C4 | Memory lag negligible: `τ → 0` | No history term |
| C5 | `L_CG ≪ L_source` | Coarse-graining scale smaller than source scale |

**None of C1–C5 are derived from QNG dynamics.** They are conditions imposed from the outside to make QNG match Newtonian gravity. Without an independent dynamical equation for Σ sourced by matter (analogous to Poisson's equation), QNG does not predict `∇²Σ = 2πGρ` — it assumes it or is silent on it.

**This is the largest current gap in the theory: QNG has no first-principles equation of motion for Σ itself.**

---

## Part 2 — Conditions for Relativistic Metric Structure

### 2.1 Why the Current Metric is Not Relativistic

The v3 QNG metric is:
- 2-dimensional (spatial only)
- Riemannian (positive definite, signature `(+,+)`)
- Defined at a fixed time t

A relativistic spacetime metric requires:
- 4-dimensional (3+1)
- Lorentzian (signature `(−,+,+,+)`)
- Satisfies Einstein field equations: `G_μν = 8πG T_μν`

These are not currently satisfied.

### 2.2 Candidate Extension: 4D Hessian

Attempt to extend: let `Σ(x, t)` be a spacetime scalar field. Define the covariant 4D Hessian:

```
H_μν = ∇_μ ∇_ν Σ
```

where `∇_μ` is the covariant derivative on the background spacetime.

Candidate 4D metric:

```
g_μν = -H_μν / normalization
```

For this to be Lorentzian, we need `H_μν` to have signature `(+,−,−,−)` (one positive, three negative eigenvalues), which requires:

```
∂_t² Σ > 0    (timelike direction: Σ has upward curvature in time)
∂_i ∂_j Σ < 0  (spacelike directions: Σ has downward curvature in space, i.e. concave)
```

Combining: Σ is concave in space but convex in time — like a wave crest moving forward.

**Physical interpretation:** Σ would behave like a propagating wave with a specific dispersion relation determined by the balance of temporal and spatial curvatures.

**Condition for Lorentzian signature:**

```
∂_t² Σ_s > |λ_min(-Hess_spatial(Σ_s))|
```

where `λ_min` is the smallest spatial eigenvalue. This is not guaranteed and would require a dynamical equation for `Σ`.

### 2.3 Relation to Scalar Gravity Theories

The form `g_μν ∝ -∂_μ ∂_ν Σ` has structural similarity to:

- **Nordström gravity (1913):** conformally flat metric `g_μν = φ² η_μν`. Different form, but same spirit (scalar → metric).
- **Einstein-dilaton theories:** scalar field φ couples to curvature via `R + (∇φ)²` action.
- **Brans-Dicke theory:** scalar φ multiplies the Einstein-Hilbert action.

QNG differs from all of these because:
1. The metric is not conformally related to flat space (the Hessian structure is richer)
2. Σ is a stability/memory field, not an independent scalar with its own kinetic term

**For GR to emerge from QNG**, one would need to show that the Einstein tensor `G_μν[g_QNG]` sourced by the energy-momentum of the Σ field reproduces the standard GR result in some limit. This has not been attempted.

### 2.4 Minimal Requirements for Relativistic Emergence

For a rigorous relativistic emergence claim, QNG would need:

1. **A 4D metric ansatz** (above sketch, needs formalization)
2. **An equation of motion for Σ** (currently absent — this is the critical missing piece)
3. **A stress-energy tensor T_μν[Σ]** derived from a Lagrangian for the Σ field
4. **A proof that `G_μν[g_QNG] ≈ 8πG T_μν`** in some limit

None of these exist in v1. The relativistic extension is an open research direction, not a current claim.

---

## Part 3 — Whether χ = m/c Can Appear Naturally

### 3.1 Current Status

In QNG v1: `τ_i = α_τ χ_i`, `χ_i = m_i / c` — this is an ansatz, not derived.

Dimensional check: `[τ] = s`, `[α_τ] = m/kg`, `[χ] = kg·s/m = kg/c` in SI units.

In natural units `c = 1`: `χ = m` (rest mass). The factor `1/c` is purely dimensional.

### 3.2 Conditions for Natural Emergence

For `χ = m/c` to appear naturally from QNG, one of the following paths would need to work:

**Path A — Variational principle:**

Define an action for the memory sector:

```
S_memory = ∫ τ(x) · [(v · ∇) ∇Σ]² dV dt
```

Require S_memory to be dimensionless (in natural units) and Lorentz-invariant. The coupling `τ` would then be determined by the invariant mass of the node. In 4D with `[Σ] = 1` (dimensionless), `[(v·∇)∇Σ]² = m⁻⁴` → `[τ] = m⁴` (in natural units where `[x] = m⁻¹`). This does not immediately give `τ = m/c`.

**Path B — Lorentz invariant coupling:**

In SR, the worldline action is `S = -m c ∫ ds`. If the memory coupling is added as a correction:

```
S_total = -mc ∫ ds - ∫ (α_τ χ) a_lag · dx
```

For this to transform correctly under Lorentz boosts, `χ` must be a Lorentz scalar. The rest mass `m₀` is a Lorentz scalar. So `χ = m₀/c` would work dimensionally.

**However:** this is a post-hoc construction, not a first-principles derivation. It assumes the memory sector should couple to inertia, which is exactly what STRATON-002 tested and found NO evidence for.

**Path C — Noether charge:**

If QNG has a symmetry (e.g., scale invariance of Σ), the associated Noether charge might evaluate to `m/c`. This requires a Lagrangian for Σ (currently absent) and a symmetry group analysis.

### 3.3 Verdict

`χ = m/c` cannot currently appear naturally from QNG because:
1. No action principle exists for the full theory
2. STRATON-002 falsifies the mass-scaling prediction empirically
3. The identification is dimensional analysis dressed as physics

The honest statement: `χ` is a free parameter. Its value is to be determined from experiment, not derived from the theory.

---

## Part 4 — Failure Modes

### 4.1 Mathematical Failure: Metric Singularity

The conformal normalization:

```
g_ij = -∂_i ∂_j Σ_s / (-∇² Σ_s)
```

diverges whenever `∇² Σ_s = 0` (Σ_s is harmonic at that point).

In electrostatics, harmonic functions are exactly the solutions to Laplace's equation in vacuum. So QNG's metric is undefined precisely where there is no matter — the vacuum. This is backwards from GR, which is defined everywhere including vacuum.

**Severity:** critical. Requires either a regularization (add small ε to denominator — but this introduces a new free parameter) or a completely different normalization scheme.

### 4.2 Mathematical Failure: SPD Breakdown at Inflection Points

`-Hess(Σ_s)` is SPD only where Σ_s is strictly concave. At any inflection surface (where concavity changes sign), one eigenvalue passes through zero. The metric degenerates and `g^{ij}` diverges.

**Physical consequence:** infinite acceleration at inflection surfaces of Σ. No analogue in Newtonian or GR physics.

**Severity:** critical for dynamical stability.

### 4.3 Mathematical Failure: Self-Referential Dynamics

In the static pipeline, Σ is treated as given. In a dynamical theory:

```
m ẍ^i(t) = -g^{ij}[Σ(x,t)] ∂_j Σ(x,t)     [particle equation]
∂_t Σ(x,t) = F[{x_k(t), ẋ_k(t)}]             [Σ evolution equation — unknown]
```

The metric is a function of Σ, which evolves due to particle motion, which depends on the metric. This is a fully coupled nonlinear system.

**Current state:** F is unknown. Without it, the theory cannot make dynamical predictions. It can only describe static or quasi-static configurations.

**Severity:** critical for any dynamical test (trajectories, timing).

### 4.4 Mathematical Failure: Non-Commutativity of Smooth and Differentiate

The v3 pipeline: smooth Σ first (at scale s), then differentiate to get Hessian.

Formally: `g_ij = ∂_i ∂_j [K_s * Σ]` where `K_s` is the Gaussian kernel.

Alternative (physically motivated): differentiate first, then smooth: `g_ij = K_s * [∂_i ∂_j Σ]`

These are NOT the same unless `Σ` is band-limited at scale s. The pipeline uses the first version, but a fully consistent coarse-graining theory might require the second. The difference is:

```
Δg_ij = ∂_i ∂_j [K_s * Σ] - K_s * [∂_i ∂_j Σ]
       = [∂_i ∂_j, K_s] Σ   (commutator)
```

For a Gaussian kernel, the commutator is nonzero unless Σ is slowly varying at scale s.

**Severity:** moderate — affects quantitative predictions, not the qualitative structure.

### 4.5 Physical Failure: No Equation of Motion for Σ

The deepest gap: QNG has no derived equation governing how Σ evolves. Without this:
- The theory is kinematic, not dynamic
- Σ must be supplied externally (from data or simulation)
- No prediction for how the gravitational field responds to mass redistribution
- No analogue of the Poisson equation or Einstein equations

**Severity:** fundamental. Without this, QNG is a parametric fit, not a theory.

---

## Part 5 — Mathematically Rigorous Next Tests

### Test T-CL-001: Harmonic Sigma Singularity

**Hypothesis:** If QNG is consistent, the metric must be well-defined everywhere including near-vacuum regions where Σ_s approaches a harmonic function.

**Test:** Construct a synthetic dataset where a subset of nodes has near-zero `∇²Σ_s`. Record whether the metric estimator diverges, regularizes, or produces unphysical eigenvalues.

**Falsification:** If metric eigenvalues diverge or become negative in near-harmonic regions without SPD projection saving them, the conformal normalization scheme is broken.

**Gates:**
- `max(|g_ij|)` bounded in near-harmonic regions: PASS criterion
- Condition number `κ(g) < 1000` in near-harmonic regions: PASS criterion

---

### Test T-CL-002: Σ Equation of Motion Consistency

**Hypothesis:** The acceleration law `a = -g^{ij} ∂_j Σ` is consistent with a Lagrangian formulation. Specifically, there exists a potential `V[Σ]` such that the equations of motion derived from `L = (1/2)m|ẋ|² - V[Σ]` reproduce `a = -g^{ij} ∂_j Σ`.

**Test:** Check whether `g^{ij} ∂_j Σ = ∂V/∂x^i` for some V. This requires `g^{ij} ∂_j Σ` to be conservative (curl-free):

```
∂_k (g^{ij} ∂_j Σ) = ∂_i (g^{kj} ∂_j Σ)
```

**Falsification:** If the QNG acceleration field is non-conservative (non-zero curl), no potential exists, and the motion is dissipative — fundamentally inconsistent with conservative gravity.

**Computable:** yes, from existing pipeline artifacts.

---

### Test T-CL-003: Poisson Equation for Σ

**Hypothesis:** If QNG reduces to Newtonian gravity, then Σ must satisfy a Poisson-like equation sourced by matter density ρ.

**Test:** For a known mass distribution ρ (e.g., the synthetic datasets DS-002/DS-003), compute `∇²Σ_s` at each node and compare with `2πG ρ_node`. Measure correlation.

**Falsification:** If `∇²Σ_s` is uncorrelated with `ρ` across nodes (Pearson r < 0.5, p < 0.01), then Σ does not encode gravity in the Newtonian sense — the theory has no Newtonian limit.

**Computable:** yes, requires density field from existing datasets.

---

### Test T-CL-004: Metric Self-Consistency Under Iteration

**Hypothesis:** In a dynamical theory, `g` depends on `Σ` which depends on particle positions which depend on `g`. The fixed-point equation is:

```
g* = G[Σ[x[g*]]]
```

**Test:** Starting from `g_0 = g0` (flat), iterate:
1. Compute `x(t)` from `a = -g_n^{ij} ∂_j Σ`
2. Update `Σ` from `x(t)` (using a simple kernel)
3. Recompute `g_{n+1}` from new `Σ`
4. Check convergence: `‖g_{n+1} - g_n‖_F < ε`

**Falsification:** If iteration diverges for all tested initial conditions and kernel choices, the dynamical QNG system has no stable fixed point — the theory predicts no static solutions, which contradicts the observed near-static universe at large scales.

---

### Test T-CL-005: χ-Independence Falsification (Critical)

**Hypothesis (null):** Lag amplitude is independent of spacecraft mass. I.e., `τ = τ_0 = const` across missions.

**Test:** This is exactly STRATON-002. Currently FAIL for mass-dependent τ (which means the null hypothesis is NOT rejected — mass scaling is not supported).

**What would falsify the null:** A dataset with ≥ 10 missions spanning mass range > 10x, with published OD residuals (not placeholders), returning `delta_BIC(mass model) < -10` and `alpha_CV < 0.3`.

**Current status:** open. STRATON-002 fails to reject mass-independence. More data needed.

---

## Summary of Derivation Status

| Claim | Status | Critical dependency |
|---|---|---|
| QNG → Newtonian at zeroth order | Partially derived (weak-field, isotropic Σ) | Requires Σ to satisfy Poisson eq. — not derived |
| Conformal normalization is consistent | Conditional | Fails where ∇²Σ = 0 (harmonic vacuum) |
| Relativistic structure can emerge | Speculative sketch | Requires 4D Σ, Lorentzian signature conditions, EOM for Σ |
| χ = m/c appears naturally | NOT derived | STRATON-002 FAIL; no action principle |
| Self-consistent dynamics | Open | No equation of motion for Σ — fundamental gap |
| Conservative acceleration | Untested | Requires T-CL-002 curl test |

---

## Critical Missing Piece

**The theory currently lacks an equation of motion for Σ.**

Without `∂_t Σ = F[ρ, g, ...]` — a sourced field equation — QNG is not a complete theory. It is a geometric ansatz applied to a given field. Every prediction it makes assumes Σ is supplied from data or from a separate theory.

The highest-priority theoretical work is to derive or postulate a consistent field equation for Σ, analogous to:
- Poisson: `∇²Σ = source`
- Klein-Gordon: `(□ + m²)Σ = source`
- Einstein: `G_μν = 8πG T_μν`

Until this exists, QNG cannot make falsifiable predictions that go beyond fitting the observed Σ field.
