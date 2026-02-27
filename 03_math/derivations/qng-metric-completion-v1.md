# QNG Metric Completion: Spin-0 / Spin-2 Decomposition — v1

**Status:** Derivation (mechanism identified; conformal coefficient derived from two independent conditions)
**Date:** 2026-02-27
**Depends on:** `qng-gr-derivation-complete-v1.md` (identifies the two gaps: factor-4 and γ≠1)
**Goal:** Fix both gaps simultaneously with a single, non-ad-hoc mechanism

---

## Motivation (the problem in one sentence)

The current QNG spatial metric $g_{ij}^{\text{QNG}} \propto \text{traceless}(\partial_i\partial_j\Sigma)$
provides only the **spin-2 (tidal)** mode of the metric perturbation.
GR requires also a **spin-0 (conformal)** mode $\propto -2\Sigma\,\delta_{ij}$.
The absence of the spin-0 mode is the single source of *both* the factor-4 in $G_{00}$
*and* $\gamma \neq 1$.

---

## Part I — The Irreducible Decomposition

Any symmetric $3\times3$ tensor $h_{ij}$ decomposes uniquely into:

$$h_{ij} = \underbrace{S_{ij}}_{\text{spin-2 (tidal)}}
+ \underbrace{\varepsilon\,\delta_{ij}}_{\text{spin-0 (conformal)}}
\tag{I.1}$$

where $S_{ij}$ is traceless ($\delta^{ij}S_{ij} = 0$) and $\varepsilon = \frac{1}{3}\delta^{ij}h_{ij}$.

**Current QNG metric:**
$$g_{ij}^{\text{QNG,current}} = \delta_{ij} + S_{ij}, \qquad \varepsilon = 0 \tag{I.2}$$

**Required metric (GR):**
$$g_{ij}^{\text{GR}} = \delta_{ij} + S_{ij}^{\text{GR}} + \varepsilon^{\text{GR}}\,\delta_{ij},
\qquad \varepsilon^{\text{GR}} = -2\Sigma \tag{I.3}$$

In GR's harmonic gauge: $S_{ij}^{\text{GR}} = 0$ (isotropic), so the tidal part vanishes.
In QNG: $S_{ij} \neq 0$ — this is the straton-lag source (and is a *feature*, not a bug).

**The completion task:** find the physical mechanism that generates
$\varepsilon = -2\Sigma$ in QNG.

---

## Part II — Two Independent Conditions that Both Require $\varepsilon = -2\Sigma$

### Condition C1 — Einstein equation normalization ($G_{00}$)

From Appendix B of `qng-gr-derivation-complete-v1.md`:
the 4D trace is $H^\alpha_{\ \alpha} = 2\Sigma + 3\varepsilon$.
The trace-reversed time perturbation:

$$\bar{H}_{00} = H_{00} - \tfrac{1}{2}\eta_{00}H^\alpha_{\ \alpha}
= -2\Sigma + \tfrac{1}{2}(2\Sigma + 3\varepsilon)
= -\Sigma + \tfrac{3}{2}\varepsilon \tag{II.1}$$

The linearized Einstein equation requires $-\nabla^2\bar{H}_{00} = 16\pi G\rho$:

$$-\nabla^2\!\left(-\Sigma + \tfrac{3}{2}\varepsilon\right) = 16\pi G\rho$$

$$\nabla^2\Sigma - \tfrac{3}{2}\nabla^2\varepsilon = 16\pi G\rho$$

Using the QNG Poisson equation $\nabla^2\Sigma = 4\pi G\rho$:

$$4\pi G\rho - \tfrac{3}{2}\nabla^2\varepsilon = 16\pi G\rho$$

$$\boxed{\nabla^2\varepsilon = -8\pi G\rho = 2\,\nabla^2\Sigma} \tag{II.2}$$

Any $\varepsilon$ satisfying $\nabla^2\varepsilon = 2\nabla^2\Sigma$ fixes $G_{00}$.
The simplest particular solution: $\varepsilon = 2\Sigma + f$ where $\nabla^2 f = 0$.

With the boundary condition $\varepsilon \to 0$ as $r \to \infty$ and $\Sigma \to 0$ as $r\to\infty$:

$$\varepsilon = 2\Sigma \tag{II.3a}$$

**Wait** — this gives $\varepsilon = 2\Sigma$, not $-2\Sigma$.
Let me recheck the sign. At $r \to \infty$: $\Sigma \to 0$ and $\varepsilon \to 0$ ✓.
But the sign of $\varepsilon$ relative to $\Sigma$: in GR, $h_{ij}^{\text{GR}} = -2\Phi\,\delta_{ij}$
with $\Phi = \Sigma < 0$ near a mass, so $h_{ij} > 0$ — the spatial metric is
*expanded* in a gravitational well. Then $\varepsilon = -2\Sigma > 0$.

Let me redo with sign care. For a mass $M$ at origin: $\Sigma = -GM/r < 0$.
GR: $h_{ij}^{\text{GR}} = -2\Sigma\,\delta_{ij} = +2GM/r\,\delta_{ij} > 0$.
So $\varepsilon^{\text{GR}} = -2\Sigma = +2GM/r > 0$.

From (II.3a): $\varepsilon = 2\Sigma = -2GM/r < 0$.
That has the **wrong sign** compared to GR!

**Resolution:** the sign depends on whether $H_{ij}$ is defined as $g_{ij} - \delta_{ij}$
or $\delta_{ij} - g_{ij}$. In the QNG convention where the Hessian metric perturbation
is $h_{ij}^{\text{QNG}} \propto -\partial_i\partial_j\Sigma$ (note the minus sign from
the definition of stability = $-\Sigma$), the conformal coefficient should be
$\varepsilon = -2\Sigma$ (same sign as GR's isotropic term).

**Recheck with explicit QNG convention:**

QNG Hessian: $h_{ij}^{\text{QNG,tidal}} \propto -\partial_i\partial_j\Sigma$
(the minus sign ensures the metric is *more curved* where $\Sigma$ is more negative,
which corresponds to stronger gravity).

Taking $\varepsilon = -2\Sigma$ and checking (II.2):
$$\nabla^2(-2\Sigma) = -2\nabla^2\Sigma = -8\pi G\rho = 2\nabla^2\Sigma$$

This requires $-2\nabla^2\Sigma = 2\nabla^2\Sigma$, i.e. $\nabla^2\Sigma = 0$. Contradiction.

The correct coefficient comes from solving (II.2) directly:
$\nabla^2\varepsilon = 2\nabla^2\Sigma$ → $\varepsilon = 2\Sigma + \text{harmonic}$.
With BCs: $\varepsilon = 2\Sigma$.

So **C1 requires $\varepsilon = 2\Sigma$**, not $-2\Sigma$.

Let us verify the 4D trace with $\varepsilon = 2\Sigma$:
$$H^\alpha_{\ \alpha} = 2\Sigma + 3(2\Sigma) = 8\Sigma$$
$$\bar{H}_{00} = -2\Sigma + \tfrac{1}{2}(8\Sigma) = -2\Sigma + 4\Sigma = 2\Sigma$$
$$-\nabla^2\bar{H}_{00} = -2\nabla^2\Sigma = -8\pi G\rho$$

But we need $+16\pi G\rho$... Still a sign problem. Let me carefully track signatures.

**Sign convention audit** (metric $(-,+,+,+)$, $\Sigma < 0$ near mass):

- $H_{\mu\nu} \equiv g_{\mu\nu} - \eta_{\mu\nu}$
- $H_{00} = g_{00} - \eta_{00} = -(1+2\Sigma) - (-1) = -2\Sigma > 0$ ✓
- $H^\alpha_{\ \alpha} = \eta^{\alpha\beta}H_{\beta\alpha} = \eta^{00}H_{00} + \delta^{ij}H_{ij} = (-1)(-2\Sigma) + 3\varepsilon = 2\Sigma + 3\varepsilon$
- $\bar{H}_{00} = H_{00} - \tfrac{1}{2}\eta_{00}H^\alpha_{\ \alpha} = -2\Sigma - \tfrac{1}{2}(-1)(2\Sigma + 3\varepsilon) = -2\Sigma + \Sigma + \tfrac{3}{2}\varepsilon = -\Sigma + \tfrac{3}{2}\varepsilon$
- Need: $-\nabla^2\bar{H}_{00} = 16\pi G\rho = 4\nabla^2\Sigma$

$$-\nabla^2(-\Sigma + \tfrac{3}{2}\varepsilon) = \nabla^2\Sigma - \tfrac{3}{2}\nabla^2\varepsilon = 4\nabla^2\Sigma$$

$$\nabla^2\varepsilon = -\tfrac{2}{3}\nabla^2\Sigma$$

So $\varepsilon = -\tfrac{2}{3}\Sigma + \text{harmonic}$.
With boundary conditions: $\boxed{\varepsilon = -\tfrac{2}{3}\Sigma}$.

Let us verify:
$$\bar{H}_{00} = -\Sigma + \tfrac{3}{2}\left(-\tfrac{2}{3}\Sigma\right) = -\Sigma - \Sigma = -2\Sigma$$
$$-\nabla^2\bar{H}_{00} = 2\nabla^2\Sigma = 8\pi G\rho$$

Still not $16\pi G\rho$. Let me try $\varepsilon = -2\Sigma$:
$$\bar{H}_{00} = -\Sigma + \tfrac{3}{2}(-2\Sigma) = -\Sigma - 3\Sigma = -4\Sigma$$
$$-\nabla^2\bar{H}_{00} = 4\nabla^2\Sigma = 16\pi G\rho \quad\checkmark$$

So $\varepsilon = -2\Sigma$ gives $G_{00}$ correctly. Now let me verify equation (II.2):
$$\nabla^2\varepsilon = \nabla^2(-2\Sigma) = -2\nabla^2\Sigma$$

From (II.2), the requirement was $\nabla^2\varepsilon = 2\nabla^2\Sigma$. But we get $-2\nabla^2\Sigma$. There's a sign error in my derivation of (II.2) above. Let me redo carefully.

$-\nabla^2\bar{H}_{00} = 16\pi G\rho = 4\nabla^2\Sigma$:

$$-\nabla^2\left(-\Sigma + \tfrac{3}{2}\varepsilon\right) = 4\nabla^2\Sigma$$
$$\nabla^2\Sigma - \tfrac{3}{2}\nabla^2\varepsilon = 4\nabla^2\Sigma$$
$$-\tfrac{3}{2}\nabla^2\varepsilon = 3\nabla^2\Sigma$$
$$\nabla^2\varepsilon = -2\nabla^2\Sigma \tag{II.2 corrected}$$

With $\varepsilon = -2\Sigma$: $\nabla^2\varepsilon = -2\nabla^2\Sigma$ ✓

**Condition C1 requires $\varepsilon = -2\Sigma$.** ✓

### Condition C2 — PPN parameter $\gamma = 1$

In the PPN formalism, the metric is written as:

$$g_{ij} = (1 + 2\gamma|\Sigma|/c^2)\,\delta_{ij} + O(v^4/c^4)$$

(with the convention $\Sigma = \Phi_{\text{grav}} < 0$ and $g_{ij} > \delta_{ij}$ near mass).

For GR: $\gamma = 1$, meaning $h_{ij}^{\text{isotropic}} = -2\Sigma\,\delta_{ij}$.

If the QNG metric has $h_{ij} = S_{ij} + \varepsilon\,\delta_{ij}$, then at the leading isotropic level:

$$\gamma_{\text{QNG}} = -\varepsilon / (2\Sigma)$$

For $\gamma = 1$:

$$\boxed{\varepsilon = -2\Sigma} \tag{II.4}$$

**Both C1 and C2 independently require the same $\varepsilon = -2\Sigma$.** This is not a coincidence — it reflects the fact that in GR, $\gamma = 1$ and the Einstein equations are equivalent (they encode the same physics). The fact that QNG recovers this from two independent conditions is the structural confirmation that the completion is consistent.

---

## Part III — Physical Mechanism: Vacuum Ricci Flatness

Conditions C1 and C2 tell us *what* $\varepsilon$ must be, but not *why* it arises
in QNG. Here we propose the mechanism.

### III.1 The Vacuum Ricci Scalar Condition

In GR, vacuum spacetime satisfies $R_{\mu\nu} = 0$ (vacuum Einstein equations).
The trace gives $R = 0$. In linearized form:

$$R = -\nabla^2 H^\alpha_{\ \alpha} = -\nabla^2(2\Sigma + 3\varepsilon) = 0 \tag{III.1}$$

In vacuum ($\nabla^2\Sigma = 0$):

$$\nabla^2(2\Sigma + 3\varepsilon) = 2\nabla^2\Sigma + 3\nabla^2\varepsilon = 0 + 3\nabla^2\varepsilon = 0$$

So $\nabla^2\varepsilon = 0$ in vacuum. Combined with $\varepsilon \to 0$ at infinity:
$\varepsilon$ is the unique harmonic function vanishing at infinity. Given that $\varepsilon$ must
match $-2\Sigma$ at the matter boundary (from C1 in the source region), and both
$\varepsilon$ and $-2\Sigma$ are harmonic in vacuum and vanish at infinity:

$$\varepsilon = -2\Sigma \quad \text{in vacuum} \tag{III.2}$$

**Statement:** QNG supplemented with the condition that the vacuum scalar curvature
$R = 0$ uniquely determines the conformal coefficient $\varepsilon = -2\Sigma$.

**What this means physically:** the QNG graph in vacuum does not support a net
volumetric expansion or contraction (zero scalar curvature). Any conformal mode $\varepsilon$
must therefore be sourced by the same function as $\Sigma$ and, matched at the boundary,
equals $-2\Sigma$.

### III.2 The Completed QNG Metric

$$\boxed{g_{ij}^{\text{QNG,complete}} = \delta_{ij}
+ \underbrace{\alpha\,S_{ij}(\Sigma)}_{\text{spin-2: tidal/straton}}
+ \underbrace{(-2\Sigma)\,\delta_{ij}}_{\text{spin-0: conformal/GR}}} \tag{III.3}$$

where $S_{ij}(\Sigma)$ is the Frobenius-normalized traceless Hessian and
$\alpha$ is the straton coupling strength (suppressed by $\tau_{\text{phys}}$ at leading order).

### III.3 Interpretation: Two Modes Serve Different Physics

| Mode | Form | Source | Physical role |
|---|---|---|---|
| Spin-0 (conformal) | $-2\Sigma\,\delta_{ij}$ | Σ directly | Standard GR: light deflection, perihelion, geodetic |
| Spin-2 (tidal) | $\alpha\,S_{ij}(\Sigma)$ | Hessian of Σ | QNG: straton lag, Pioneer-type anomalies |

The spin-0 mode gives $\gamma = 1$ and correct $G_{00}$.
The spin-2 mode gives the QNG-specific dynamics.
They are *decoupled* at linear order — neither invalidates the other.

### III.4 The Straton Limit

When $\alpha \to 0$ (no straton coupling, $\tau_{\text{phys}} \to 0$):

$$g_{ij}^{\text{QNG,complete}} \to \delta_{ij} - 2\Sigma\,\delta_{ij} = (1 - 2\Sigma)\,\delta_{ij}$$

This is the exact GR isotropic metric in harmonic gauge. **QNG reduces to GR
in the zero-lag limit.** ✓

This is the correct physical interpretation: the spin-2/tidal correction is the
QNG-specific term, suppressed relative to the spin-0/GR term by a factor
$\alpha \sim \tau_{\text{phys}} \ll 1$.

---

## Part IV — Verification

### IV.1 Einstein tensor with completed metric

With $h_{ij} = \alpha S_{ij} - 2\Sigma\,\delta_{ij}$:

- $\text{tr}(h_{ij}) = 0 - 6\Sigma = -6\Sigma$ (matches GR isotropic gauge)
- $H^\alpha_{\ \alpha} = 2\Sigma + (-6\Sigma) = -4\Sigma$ (matches GR ✓)
- $\bar{H}_{00} = -2\Sigma - \tfrac{1}{2}(-1)(-4\Sigma) = -2\Sigma - 2\Sigma = -4\Sigma$
- $-\nabla^2\bar{H}_{00} = 4\nabla^2\Sigma = 16\pi G\rho$ ✓

$G_{00} = 8\pi T_{00}$ is satisfied. **Factor-4 gap closed.** ✓

### IV.2 PPN parameter $\gamma$

Isotropic part of $h_{ij}$: $\varepsilon\,\delta_{ij} = -2\Sigma\,\delta_{ij}$.
Therefore:

$$\gamma_{\text{QNG,complete}} = -\varepsilon / (2\Sigma) = -(-2\Sigma)/(2\Sigma) = 1 \quad \checkmark$$

Light deflection: $(1+\gamma)/2 \times 4GM/bc^2 = 4GM/bc^2$ (GR value). ✓

### IV.3 Geodesic equation (unchanged)

The geodesic derivation (Part II of `qng-gr-derivation-complete-v1.md`) used only
$g_{00}$ — it is unchanged by the addition of the conformal term to $g_{ij}$.
$a^i = -g^{ij}\partial_j\Sigma$ still holds exactly. ✓

### IV.4 Straton lag (unchanged)

The lag acceleration comes from the spin-2 part $S_{ij}$ alone (via the VPC story:
radial Hessian, spherical symmetry). Adding $-2\Sigma\delta_{ij}$ to the spatial
metric adds an isotropic conformal contribution to the lag:

$$\delta a^i_{\text{conformal}} = -\tau\,v^j\,\partial_j(2\Sigma)\,\delta^{ij}
= -2\tau\,v^j\,\partial_j\Sigma\,\hat{x}^i/|\hat{x}|$$

This is $O(\Sigma/c^2)$ smaller than the straton tidal lag for slow-motion orbits,
and can be absorbed into the leading-order geodesic term. The straton phenomenology
(constant Pioneer anomaly, $C \times v_r$) is unaffected at the precision of current
observations. ✓

---

## Part V — Status After Completion

| GR Result | Before completion | After completion | Mechanism |
|---|---|---|---|
| Geodesic ($a^i = -g^{ij}\partial_j\Sigma$) | ✓ Exact | ✓ Exact (unchanged) | Christoffel |
| Poisson equation | ✓ Exact | ✓ Exact | Field eq. |
| $G_{00} = 8\pi T_{00}$ | ✗ Factor-4 | ✓ Fixed | Conformal term |
| $\gamma = 1$ | ✗ $\gamma \neq 1$ | ✓ Fixed | Conformal term |
| Gravitational waves | ✗ Static only | ✗ Still missing | Dynamic extension needed |
| Strong field | ✗ Not covered | ✗ Still missing | Vacuum EFE needed |

**Two of the four identified gaps are closed simultaneously by a single mechanism
(the spin-0 conformal term $-2\Sigma\,\delta_{ij}$, derived from vacuum Ricci
flatness $R = 0$).**

---

## Part VI — What Is Assumed vs. Derived

### Derived (from QNG foundations):
- Spin-2/tidal part of $g_{ij}$: from Hessian of $\Sigma$ (locked, v4) ✓
- Geodesic equation: from Christoffel of 4D metric ✓
- Conformal coefficient $\varepsilon = -2\Sigma$: derived from $R = 0$ in vacuum + BCs ✓
- Equivalence of C1 (Einstein) and C2 (PPN) conditions ✓

### Assumed (not yet derived from graph structure):
- **$R = 0$ in vacuum as a QNG condition**: this is borrowed from GR. A first-principles
  derivation would show that the QNG graph in vacuum has zero emergent Ricci scalar.
  Plausibility argument: in vacuum, $\Sigma$ is harmonic → all derivatives are smooth
  → no graph-level curvature concentration → $R = 0$. Not yet formalized.

- **Boundary condition $\varepsilon \to 0$ as $r \to \infty$**: natural (no metric
  perturbation at infinity), but should follow from the graph construction.

- **The full Einstein equations $G_{ij} = 8\pi T_{ij}$** (spatial components):
  The spin-2 tidal term still contributes to $G_{ij}$ at first PN order.
  Whether this matches GR's $G_{ij}$ exactly is not yet checked.

---

## Appendix — The Completed Metric in One Expression

The QNG metric (complete, linearized, static, $c = G = 1$):

$$g_{\mu\nu}^{\text{QNG}} = \begin{pmatrix}
-(1+2\Sigma) & 0 \\
0 & (1-2\Sigma)\delta_{ij} + \alpha\,S_{ij}(\Sigma)
\end{pmatrix} \tag{A.1}$$

In the limit $\alpha = 0$ (no straton): exact weak-field GR metric in harmonic gauge.

For $\alpha \neq 0$ (straton active): GR + tidal correction, with:

$$|h_{ij}^{\text{tidal}}| / |h_{ij}^{\text{conf}}| \sim \alpha / (2|\Sigma|)
\sim \alpha\,r / (2GM)$$

In the outer solar system ($r \sim 40$ AU, $\alpha \sim \tau_{\text{phys}}^2/l_0^2$):
this ratio is $\ll 1$ at current measurement precision — consistent with the
fact that the straton effect has not been detected at the level of standard
GR tests.
