# QNG ε-from-Graph Derivation — Candidate Approaches v1

- Date: 2026-02-27
- Authored by: Claude Sonnet 4.6
- Status: PROPOSED (not implemented; none selected)
- Context: The conformal coefficient `ε = -2Σ` is currently **postulated** from
  boundary conditions (GR normalization + PPN γ=1). This document proposes three
  candidate derivations that would make ε **emerge** from QNG graph dynamics.

**Background:** In the v5 metric lock (`01_notes/metric/metric-lock-v5.md`), the
spatial metric is:

```
g_ij^v5 = (1 - 2Σ) δ_ij + α S_ij
```

The traceless part `S_ij` emerges naturally from the Hessian of Σ. The conformal
part `ε = -2Σ` is presently added as an external requirement. Each candidate below
proposes a mechanism by which `ε = -2Σ` would emerge without postulation.

---

## Candidate A — Graph Action Principle (Energy/Action)

### Core Idea

Construct a QNG graph action functional `I[Σ, g]` and require stationarity with
respect to the metric. The variation `δI/δg_ij = 0` yields an equation of motion
for `g_ij` that contains both spin-2 (from Hessian) and spin-0 (conformal) modes.

### Proposed Form

```
I[Σ, g] = Σ_{edges (i,j)} w_ij [ (Σ_i - Σ_j)² / g(e_ij, e_ij) ]
         + λ Σ_nodes i [ (g_ij^{iso} + 2Σ_i δ_ij)² ]
```

where:
- First term: kinetic energy of Σ measured by the metric (geodesic Dirichlet energy).
- Second term: Lagrange-multiplier-like penalty enforcing `g^{iso} = -2Σ δ`.
- `g^{iso} = (tr g / n) δ` is the isotropic projection of `g`.
- `λ` is a coupling constant with dimensions `[energy/length²]`.

Stationarity in `g`:
- Variation w.r.t. traceless modes → Hessian equation (produces `S_ij`).
- Variation w.r.t. conformal mode → `g^{iso} = -2Σ δ` (produces `ε = -2Σ`).

### Assumptions

1. The QNG graph has a well-defined scalar field `Σ` and a (possibly emergent) 2-tensor `g_ij`.
2. The Dirichlet energy term is the correct kinetic functional (equivalent to discretizing `∫|∇Σ|²_g dV`).
3. The conformal penalty term has a physical interpretation — e.g., it enforces
   vacuum Ricci flatness `R[g] = 0` in the weak-field limit.
4. `λ → ∞` enforces the constraint exactly; finite `λ` gives a relaxed version
   with `g^{iso} = -2Σ δ + O(1/λ)`.

### Falsifier

If this mechanism is correct, then:
- Numerical minimization of `I[Σ, g]` on the synthetic graphs (DS-002, DS-003, DS-006)
  should yield `ε ≈ -2Σ` at each anchor, without the explicit conformal term being coded.
- **Falsified** if: varying `Σ` field while holding the graph fixed changes `ε` at a rate
  different from `-2`, i.e., `dε/dΣ ≠ -2`.
- Confound to rule out: the penalty term trivially enforces `ε = -2Σ` by construction —
  must show `λ` is determined by the same action (e.g., from Ricci flatness), not free.

---

## Candidate B — Coarse-Graining Operator ⟨·⟩_s

### Core Idea

At fine scales, the metric is anisotropic (tidal/traceless). Under coarse-graining by
averaging over orientations or spatial scale, the traceless modes cancel and only the
isotropic (spin-0) mode survives. The surviving mode is `⟨g_ij⟩_s ≈ f(Σ) δ_ij`,
and the function `f(Σ) = 1 - 2Σ` can be determined from the coarse-grained Poisson
equation.

### Proposed Mechanism

Define the coarse-graining operator at scale `s` as:
```
⟨g_ij⟩_s(x) = ∫ K_s(x - x') g_ij(x') dV(x') / ∫ K_s(x - x') dV(x')
```
where `K_s` is the Gaussian kernel already used for Σ smoothing.

**Two-step argument:**

*Step 1 (traceless cancellation):* For a nearly isotropic distribution of anchor
orientations, `⟨S_ij⟩_s → 0` as `s → ∞`. The traceless part averages to zero
over orientations (like spin-2 modes in a rotationally symmetric ensemble).
Formally: if the graph is statistically isotropic at large scales, `⟨S_ij⟩_s = 0`
by symmetry.

*Step 2 (conformal mode from Poisson):* After coarse-graining, the surviving metric
is `⟨g_ij⟩_s = f(Σ) δ_ij`. Substituting into the coarse-grained QNG force equation:
```
a_i = -g^{ij}(coarse) ∂_j Σ  =  -f(Σ)^{-1} ∂_i Σ
```
For this to match the Newtonian limit `a_i = -∂_i Σ`, require `f(Σ) = 1 + O(Σ)`.
The GR-compatible choice is `f(Σ) = 1 - 2Σ` (from the weak-field expansion of the
inverse metric).

### Assumptions

1. The graph is **statistically isotropic** at scales `s ≫ s₀` (large-scale average
   orientation is uniform). This is an assumption about the background graph structure,
   not about the Σ field.
2. The Gaussian coarse-graining kernel `K_s` is the same kernel used to smooth Σ —
   this is already implemented in `smooth_sigma_local()`.
3. The correction `f(Σ) = 1 - 2Σ` follows from requiring the coarse-grained metric
   to reproduce the weak-field gravitational acceleration — i.e., from the geodesic
   equation, not an independent assumption.
4. The statistical isotropy assumption (1) is violated near point masses (strong-field)
   and along filaments in the graph — these are the regions where tidal effects dominate.

### Falsifier

- **Test:** Run D2 gate (coarse-grain drift) on anisotropic vs isotropic graphs
  (vary k-NN connectivity geometry). If `⟨S_ij⟩_s → 0` as `s` grows for isotropic
  graphs but not for anisotropic ones, this supports Step 1.
- **Test:** Regress `⟨g_ij⟩_s^{iso}` against `Σ_center` across anchors for large `s`.
  Slope `d⟨g^{iso}⟩/dΣ` should be `-2`. If slope ≠ -2 or is Σ-independent, falsified.
- **Confound:** The current pipeline already adds `ε = -2Σ` in v5 explicitly. To test
  Candidate B, must run the pipeline **without** the explicit conformal term and measure
  `⟨g^{iso}⟩` as a function of Σ at large scales.

---

## Candidate C — Vacuum Ricci Flatness from Graph Update Rule

### Core Idea

The graph update rule (whatever produces the Σ field) implicitly enforces a
discretized version of `R[g] = 0` in vacuum. In the linearized continuum limit,
`R = 0` is equivalent to:
```
∂_i∂^i h^{μ}_{μ} = 0   (trace condition in harmonic gauge)
```
which, for static configurations, forces `tr(h_ij) = c · h_00` with a fixed constant
`c` determined by the spatial dimension. This fixes `ε`.

### Proposed Mechanism

The QNG graph update rule is hypothesized to be:
```
Σ_{t+1}(i) = f(Σ_t(neighbors of i))
```
where `f` is a local averaging/smoothing operation. In the continuum limit, this is:
```
∂_t Σ = -τ (Laplacian_g Σ - source)
```
i.e., a Poisson/relaxation equation with metric-dependent Laplacian.

Now require that the metric `g_ij` is **self-consistent**: the metric that defines the
Laplacian in the Σ update equation is the same metric that emerges from the Σ Hessian.
This self-consistency condition is:
```
g_ij^{used in Laplacian} = g_ij^{from Hessian of Σ}
```

In the linearized weak-field limit, the self-consistent solution is:
```
g_ij^{self-consistent} = (1 - 2Σ) δ_ij + traceless   =>   ε = -2Σ
```
because this is the unique isotropic metric perturbation compatible with the Poisson
equation `∇²Σ = -4πGρ` and the Ricci flatness `R_ij^{vacuum} = 0`.

### Assumptions

1. The QNG graph update rule is (or converges to) a Poisson-type relaxation equation
   in the continuum limit. This assumption is about the large-scale behavior of the
   discrete update rule — not derived from first principles.
2. Self-consistency of metric and Laplacian is a physical requirement (the metric is
   not merely a post-hoc observable but feeds back into the dynamics).
3. In vacuum (`ρ = 0`), the Ricci scalar `R = 0` is enforced by the update rule
   (not postulated).
4. The linearization is valid (weak-field `|Σ| ≪ 1`), which holds for the synthetic
   datasets (Σ_max ≈ 0.75 in the pipeline — marginally weak-field).

### Falsifier

- **Algebraic test:** Starting from `g_ij = δ_ij + h_ij` with `h_ij = ε δ_ij + α S_ij`,
  compute `R[g]` to linear order and verify `R = 0` forces `ε = -2Σ` uniquely.
  (This is a pen-and-paper computation; it does not require new code.)
- **Numerical test:** Implement the self-consistent iteration:
  1. Start with `g_ij^{(0)} = δ_ij`.
  2. Compute `Σ^{(k+1)}` by solving `∇²_{g^{(k)}} Σ = -4πGρ`.
  3. Extract `g_ij^{(k+1)}` from `Σ^{(k+1)}` Hessian + conformal mode.
  4. Iterate until convergence.
  Check: does the converged `ε^*` approach `-2Σ`?
- **Falsified if:** The self-consistent iteration converges to `ε ≠ -2Σ`, or if R = 0
  in vacuum does not uniquely determine ε (e.g., if there are other solutions).

---

## Comparison Table

| Criterion | Candidate A (Action) | Candidate B (Coarse-grain) | Candidate C (Ricci flatness) |
|-----------|---------------------|--------------------------|------------------------------|
| First-principles? | Partial (requires action form) | Partial (requires stat. isotropy) | Partial (requires self-consistency) |
| New code needed? | Yes (variational solver) | Yes (large-scale limit test) | Yes (self-consistent iteration) |
| Pen-and-paper check? | Partial | No | Yes (falsifier 1) |
| Connects to existing pipeline? | Via energy functional | Via D2 gate extension | Via Poisson solver in Σ |
| Most falsifiable? | Yes (λ must be derived) | Yes (isotropy testable) | Yes (R=0 computation) |
| Most physically motivated? | Medium | High (emergent symmetry) | High (GR vacuum condition) |
| Recommended priority | 3rd | 2nd | **1st** |

---

## Recommended Next Step

**Candidate C first:** The algebraic falsifier (compute R[g] at linear order, show
R = 0 forces ε = -2Σ) requires no new code and can be done analytically. If it
succeeds, it provides a clean derivation of ε from a physically meaningful condition
(vacuum Ricci flatness), without invoking statistical isotropy (B) or a free coupling
constant (A).

After Candidate C algebraic check:
- If it succeeds → formalize as `qng-epsilon-ricci-derivation-v1.md`
- If it fails (R=0 does not uniquely fix ε) → proceed to Candidate B numerical test

Candidate A is the most speculative (introduces a new action functional) and should
be deferred until B and C are exhausted.

---

## What This Document Is NOT

This document does NOT implement any of the candidates above. The v5 metric lock
uses `ε = -2Σ` as a **postulate** justified by two observational requirements (G₀₀
normalization, γ = 1). The candidates here are paths to a first-principles derivation.
None of them are pre-registered or gate-validated yet.
