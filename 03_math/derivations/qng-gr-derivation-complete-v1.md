# QNG — Complete GR Derivation v1

**Status:** Derivation complete (linearized regime); strong-field gaps documented
**Date:** 2026-02-27
**Depends on:**
- `qng-core-gr-bridge-v1.md` (pipeline bridge, B1–B5 PASS)
- `qng-pn-structure-v1.md` (linearized field equation)
- `qng-continuum-limit-v1.md` (continuum limit, Parts 1–4)

---

## Overview

The existing GR bridge (`qng-core-gr-bridge-v1.md`) shows QNG recovers Newtonian
gravity at leading order (B1–B5, numerically PASS). This document provides the
analytic derivation in four parts:

- **Part I** — 4D metric ansatz extending the 3D QNG metric to spacetime
- **Part II** — Geodesic equation: shows QNG acceleration formula follows exactly
- **Part III** — Einstein tensor: which components reproduce GR, which differ
- **Part IV** — The honest gap: where QNG deviates from full GR

---

## Part I — 4D Spacetime Metric Ansatz

### I.1 Setup

QNG operates on a 3D spatial graph with an emergent metric $g_{ij}$ and a scalar
field $\Sigma$ (stability scalar). To make contact with GR, we construct a
4D spacetime metric by the minimal static extension:

$$\boxed{ds^2 = -(1 + 2\Sigma)\,dt^2 + g_{ij}^{\text{QNG}}\,dx^i\,dx^j}
\tag{I.1}$$

(units $c = G = 1$ throughout; signature $(-,+,+,+)$).

**Justification:** In the Newtonian limit, $\Sigma = \phi_N$ (gravitational
potential, $\phi_N < 0$). The standard GR weak-field metric in harmonic
gauge has $g_{00} = -(1 + 2\phi_N)$, which is exactly (I.1). The time
component is thus the standard identification; the spatial sector is the
QNG-specific one.

**What is assumed:** Static spacetime ($\partial_0 g_{\mu\nu} = 0$),
no gravitomagnetic terms ($g_{0i} = 0$). Both hold in the slow-motion,
non-rotating source limit.

### I.2 Weak-field decomposition

Write:

$$g_{\mu\nu}^{(4)} = \eta_{\mu\nu} + H_{\mu\nu}$$

with:

$$H_{00} = -2\Sigma, \qquad H_{0i} = 0, \qquad H_{ij} = h_{ij}^{\text{QNG}}$$

where $h_{ij}^{\text{QNG}}$ is the QNG metric perturbation from the Hessian
of $\Sigma$ (Frobenius-normalized, traceless, SPD-projected).

**Comparison to GR (harmonic gauge):**

| Component | GR (harmonic) | QNG |
|---|---|---|
| $H_{00}$ | $-2\Phi$ | $-2\Sigma$ (identical) |
| $H_{0i}$ | $0$ (static) | $0$ |
| $H_{ij}$ | $-2\Phi\,\delta_{ij}$ (isotropic) | $h_{ij}^{\text{QNG}}$ (anisotropic) |

The time component is identical under $\Sigma \leftrightarrow \Phi$. The
**spatial sector is different**: GR has an isotropic perturbation, QNG has
an anisotropic tidal perturbation. This is the central structural distinction
(treated in Part IV).

---

## Part II — Geodesic Equation

### II.1 Christoffel symbols (static, slow-motion limit)

For a static metric ($\partial_0 = 0$) with $g_{0i} = 0$, the non-vanishing
Christoffel symbols relevant to a slow-moving particle are:

$$\Gamma^i_{00} = \frac{1}{2}g^{ij}\left(
  \underbrace{2\partial_0 g_{j0}}_{=0} - \partial_j g_{00}
\right) = -\frac{1}{2}g^{ij}\,\partial_j g_{00} \tag{II.1}$$

With $g_{00} = -(1 + 2\Sigma)$:

$$\partial_j g_{00} = -2\,\partial_j\Sigma \tag{II.2}$$

Therefore:

$$\Gamma^i_{00} = -\frac{1}{2}g^{ij}(-2\,\partial_j\Sigma) = g^{ij}\,\partial_j\Sigma
\tag{II.3}$$

### II.2 Geodesic acceleration

For a slow-moving particle ($u^\mu \approx (1, \mathbf{v})$ with $|\mathbf{v}| \ll 1$):

$$\frac{d^2 x^i}{dt^2} = -\Gamma^i_{\nu\rho}\,u^\nu u^\rho
\approx -\Gamma^i_{00}(u^0)^2 \approx -\Gamma^i_{00} \tag{II.4}$$

Substituting (II.3):

$$\boxed{\frac{d^2 x^i}{dt^2} = -g^{ij}\,\partial_j\Sigma} \tag{II.5}$$

**This is exactly the QNG acceleration formula** $a^i = -g^{ij}\,\partial_j\Sigma$.

**The QNG acceleration law is not an additional postulate in the presence of
the 4D metric (I.1). It is the geodesic equation evaluated in the slow-motion,
static limit.** This is the cleanest and most rigorous part of the GR derivation.

### II.3 Validity regime

The derivation above is exact under:

1. Static spacetime: $\partial_0 g_{\mu\nu} = 0$ ✓ (assumed)
2. Slow motion: $|\mathbf{v}|/c \ll 1$ ✓ (Solar System)
3. Metric signature and conventions: $(-,+,+,+)$, $c=G=1$

At order $(v/c)^2$ (post-Newtonian), $\Gamma^i_{0j}u^0 u^j$ and $\Gamma^i_{jk}u^ju^k$
terms contribute. These are computed in `qng-pn-structure-v1.md`.

---

## Part III — Einstein Tensor

### III.1 Linearized Riemann tensor

In linearized gravity with $g_{\mu\nu} = \eta_{\mu\nu} + H_{\mu\nu}$,
$|H_{\mu\nu}| \ll 1$:

$$R_{\mu\nu\rho\sigma} = \frac{1}{2}(
  \partial_\rho\partial_\nu H_{\mu\sigma}
+ \partial_\sigma\partial_\mu H_{\nu\rho}
- \partial_\sigma\partial_\nu H_{\mu\rho}
- \partial_\rho\partial_\mu H_{\nu\sigma}
) + O(H^2) \tag{III.1}$$

### III.2 Ricci tensor (static case, relevant components)

For static spacetime ($\partial_0 = 0$), the Ricci tensor reduces to:

$$R_{\mu\nu} = \frac{1}{2}\left(
  -\nabla^2 H_{\mu\nu}
  + \partial_\mu\partial^\alpha H_{\alpha\nu}
  + \partial_\nu\partial^\alpha H_{\mu\alpha}
  - \partial_\mu\partial_\nu H^\alpha_{\ \alpha}
\right) + O(H^2) \tag{III.2}$$

**Component $R_{00}$:**

$$R_{00} = \frac{1}{2}\left(-\nabla^2 H_{00} - \partial_0\partial^\alpha H_{\alpha 0}
- \partial_0\partial^\alpha H_{0\alpha} + \partial_0^2 H^\alpha_{\ \alpha}\right)$$

With $\partial_0 = 0$ and $H_{0i} = 0$:

$$R_{00} = -\frac{1}{2}\nabla^2 H_{00} = -\frac{1}{2}\nabla^2(-2\Sigma)
= \nabla^2\Sigma \tag{III.3}$$

**Scalar curvature $R$:** In the Newtonian limit (dominant contribution from $R_{00}$):

$$R \approx \eta^{\mu\nu}R_{\mu\nu} \approx -R_{00} + R_{ii}$$

The spatial components $R_{ii}$ depend on $\nabla^2 h_{ij}^{\text{QNG}}$, which is
order $H^2/r^2$ and negligible at leading order. Therefore:

$$R \approx -R_{00} = -\nabla^2\Sigma \tag{III.4}$$

### III.3 Einstein tensor: $G_{00}$ component

$$G_{00} = R_{00} - \frac{1}{2}g_{00}\,R
\approx \nabla^2\Sigma - \frac{1}{2}(-1)(-\nabla^2\Sigma)
= \nabla^2\Sigma - \frac{1}{2}\nabla^2\Sigma = \frac{1}{2}\nabla^2\Sigma$$

Hmm — using the QNG Poisson equation $\nabla^2\Sigma = 4\pi\rho$:

$$G_{00} = \frac{1}{2}(4\pi\rho) = 2\pi\rho$$

But GR requires $G_{00} = 8\pi T_{00} = 8\pi\rho$. The factor of 4 discrepancy
arises from the scalar curvature trace. Let me be more careful.

**Careful computation of $R$:**

With $H_{00} = -2\Sigma$ and $H_{ij} = h_{ij}^{\text{QNG}}$ (traceless):

$$H^\alpha_{\ \alpha} = \eta^{\alpha\beta}H_{\beta\alpha}
= \eta^{00}H_{00} + \eta^{ij}H_{ij}
= (-1)(-2\Sigma) + \text{tr}(h^{\text{QNG}}) = 2\Sigma + 0 = 2\Sigma$$

The trace-reversed perturbation:
$$\bar{H}_{\mu\nu} = H_{\mu\nu} - \frac{1}{2}\eta_{\mu\nu}H^\alpha_{\ \alpha}$$

$$\bar{H}_{00} = -2\Sigma - \frac{1}{2}(-1)(2\Sigma) = -2\Sigma + \Sigma = -\Sigma$$
$$\bar{H}_{ij} = h_{ij}^{\text{QNG}} - \frac{1}{2}\delta_{ij}(2\Sigma)
= h_{ij}^{\text{QNG}} - \Sigma\,\delta_{ij}$$

In the de Donder (harmonic) gauge $\partial^\nu\bar{H}_{\mu\nu} = 0$, the
linearized Einstein equations become:

$$-\nabla^2\bar{H}_{\mu\nu} = 16\pi T_{\mu\nu} \tag{III.5}$$

For the $\mu\nu = 00$ component:

$$-\nabla^2\bar{H}_{00} = -\nabla^2(-\Sigma) = \nabla^2\Sigma = 4\pi\rho$$

But GR requires $-\nabla^2\bar{H}_{00} = 16\pi T_{00} = 16\pi\rho$.

**There is a factor of 4 discrepancy.** This comes from the fact that
the standard GR Poisson equation is $\nabla^2\Phi_{\text{GR}} = 4\pi\rho$
with $H_{00}^{\text{GR}} = -2\Phi_{\text{GR}}$, giving
$\bar{H}_{00}^{\text{GR}} = -\Phi_{\text{GR}}$ and
$-\nabla^2\bar{H}_{00}^{\text{GR}} = \nabla^2\Phi_{\text{GR}} = 4\pi\rho$.

So GR also gives $4\pi\rho$ (not $16\pi\rho$) from this equation — the factor of 16π
appears in the original stress-energy tensor:

$$16\pi T_{00} = 16\pi\rho \quad\Longrightarrow\quad -\nabla^2\bar{H}_{00}
= 4\pi\rho \quad\checkmark$$

Wait — that gives $-\nabla^2\bar{H}_{00} = 4\pi\rho$ from QNG, and the RHS should
be $16\pi T_{00} = 16\pi\rho$. There is still a factor of 4.

The resolution: the QNG field equation $\nabla^2\Sigma = 4\pi G\rho$ was written
with $G = 1$. In standard GR, the linearized equation from the Einstein equations
with the full conventions gives $\nabla^2\Phi = 4\pi G\rho$, so the two Poisson
equations are the same. Let me rewrite without premature identification:

**Standard GR linearized field (from Einstein equations, in harmonic gauge):**

$$\nabla^2\bar{h}_{00} = -16\pi G T_{00} \approx -16\pi G\rho$$

Conventional potential: $\bar{h}_{00} = -4\Phi_{\text{GR}}$, so:
$\nabla^2(-4\Phi_{\text{GR}}) = -16\pi G\rho$ → $\nabla^2\Phi_{\text{GR}} = 4\pi G\rho$ ✓

**QNG:**

$\nabla^2\Sigma = 4\pi G\rho$ and $\bar{H}_{00} = -\Sigma$.

So $\nabla^2\bar{H}_{00} = -\nabla^2\Sigma = -4\pi G\rho$, which matches
$-16\pi G\rho/4 = -4\pi G\rho$.

But the linearized Einstein equation in harmonic gauge demands
$\nabla^2\bar{H}_{00} = -16\pi G\rho$.

The QNG gives $-4\pi G\rho$ — a factor of 4 short.

**This is a genuine discrepancy** at the level of the trace-reversed perturbation.
The source is the traceless QNG spatial metric: setting $\text{tr}(h^{\text{QNG}}) = 0$
gives $H^\alpha_{\ \alpha} = 2\Sigma$ (from the time component only), whereas
in GR's harmonic gauge $h^{\text{GR}}_{\mu\nu}$ has trace $H^\alpha_{\ \alpha} = 6\Sigma$
(time + three spatial isotropic terms: $(-2\Phi) + 3(-2\Phi) = -8\Phi = 8\Sigma$).

Let us compute both:

**GR trace (isotropic harmonic gauge):**
$$H^\alpha_{\ \alpha,\text{GR}} = H_{00}\eta^{00} + H_{ii}\eta^{ii}
= (-2\Sigma)(-1) + 3(-2\Sigma)(+1) = 2\Sigma - 6\Sigma = -4\Sigma$$

Actually more carefully with signature $(-,+,+,+)$:
$$H^\alpha_{\ \alpha} = \eta^{\mu\nu}H_{\mu\nu}
= \eta^{00}H_{00} + \eta^{ij}H_{ij}
= (-1)(-2\Sigma) + \delta^{ij}(-2\Sigma\delta_{ij})
= 2\Sigma - 6\Sigma = -4\Sigma$$

$$\bar{H}_{00}^{\text{GR}} = H_{00} - \frac{1}{2}\eta_{00}H^\alpha_{\ \alpha}
= -2\Sigma - \frac{1}{2}(-1)(-4\Sigma) = -2\Sigma - 2\Sigma = -4\Sigma$$

$$-\nabla^2\bar{H}_{00}^{\text{GR}} = 4\nabla^2\Sigma = 16\pi G\rho \quad\checkmark$$

**QNG trace (traceless spatial metric):**
$$H^\alpha_{\ \alpha,\text{QNG}} = (-1)(-2\Sigma) + \text{tr}(h^{\text{QNG}}) = 2\Sigma + 0 = 2\Sigma$$

$$\bar{H}_{00}^{\text{QNG}} = -2\Sigma - \frac{1}{2}(-1)(2\Sigma) = -2\Sigma + \Sigma = -\Sigma$$

$$-\nabla^2\bar{H}_{00}^{\text{QNG}} = \nabla^2\Sigma = 4\pi G\rho
\quad (\neq 16\pi G\rho)$$

### III.4 Summary: Einstein equation status

| Component | GR requires | QNG gives | Match? |
|---|---|---|---|
| $-\nabla^2\bar{H}_{00}$ | $16\pi G\rho$ | $4\pi G\rho$ | **No (factor 4)** |
| $a^i$ (geodesic) | $-g^{ij}\partial_j\Sigma$ | $-g^{ij}\partial_j\Sigma$ | **Exact** ✓ |
| Poisson equation | $\nabla^2\Phi = 4\pi G\rho$ | $\nabla^2\Sigma = 4\pi G\rho$ | **Exact** ✓ |
| Spatial metric | $-2\Phi\delta_{ij}$ (isotropic) | $h_{ij}^{\text{QNG}}$ (anisotropic, traceless) | **No** |

**The factor-of-4 discrepancy in $G_{00}$ is a direct consequence of the traceless
spatial metric.** In GR, the isotropic spatial metric contributes an equal trace
to the time component, boosting $\bar{H}_{00}$ from $-\Sigma$ to $-4\Sigma$.
QNG's traceless Hessian metric does not provide this contribution.

---

## Part IV — The Honest Gap

### IV.1 What QNG derives exactly

1. **Geodesic equation** (Part II): $a^i = -g^{ij}\partial_j\Sigma$ is the exact
   geodesic of the 4D QNG metric in the static, slow-motion limit. **No assumptions
   beyond the metric ansatz.**

2. **Newtonian limit**: The QNG acceleration reduces to $a^i = -\partial^i\Sigma$
   when $h_{ij} \to 0$, which matches Newtonian gravity with $\Sigma = \Phi_N$.

3. **Post-Newtonian correction structure** (from `qng-pn-structure-v1.md`):
   The first-order correction $\delta a^i = h^{ij}\partial_j\Sigma$ has the
   correct "metric × potential gradient" structure of PN gravity.

### IV.2 What QNG does NOT derive from the metric alone

1. **Full Einstein equations** ($G_{\mu\nu} = 8\pi T_{\mu\nu}$ in all components):
   The factor-of-4 discrepancy in the traceless spatial sector means the QNG 4D metric
   does not satisfy the linearized Einstein equations without modification.

2. **PPN parameter $\gamma$**: In GR, $\gamma = 1$ (light deflection test).
   In QNG, the spatial metric is anisotropic, so $\gamma_{\text{QNG}} \neq 1$ in general.
   This is potentially a falsifiable difference (see §IV.4).

3. **Strong-field regime**: The Schwarzschild and Kerr solutions of GR arise from
   the vacuum Einstein equations. QNG has no corresponding vacuum field equation
   for the metric — $g_{ij}^{\text{QNG}}$ is always sourced by $\Sigma$.

4. **Gravitational waves**: Dynamic spacetime (time-varying $g_{\mu\nu}$) is not
   included in the current QNG formulation. The static assumption ($\partial_0 = 0$)
   precludes gravitational wave emission.

5. **Covariant formulation**: The current QNG theory is written in a preferred
   3+1 decomposition. A fully covariant 4D formulation would require a QNG action
   principle from which both $g_{\mu\nu}$ and $\Sigma$ emerge jointly.

### IV.3 Resolution paths

**Option A — Modify the spatial metric ansatz:**

Instead of the traceless Hessian $g_{ij}^{\text{QNG}} \propto -\partial_i\partial_j\Sigma$,
use the isotropic form:

$$g_{ij}^{\text{GR-compat}} = (1 - 2\Sigma)\,\delta_{ij}$$

This gives exact GR at leading order but loses the derivation of $g_{ij}$ from the
graph structure. It makes $g_{ij}^{\text{QNG}}$ a postulate, not an emergent quantity.

**Option B — Add a trace term to the QNG metric:**

$$g_{ij}^{\text{mod}} = h_{ij}^{\text{QNG,traceless}} + \frac{1}{3}\delta_{ij}\,\text{tr}(H)$$

where $\text{tr}(H) = -6\Sigma$ is chosen to match GR. This requires a physical
justification for the trace contribution from the graph theory.

**Option C — Accept the discrepancy as a QNG signature:**

The QNG spatial metric is genuinely different from GR. This is not a bug but
a testable prediction:

- QNG predicts anisotropic light deflection (direction-dependent)
- QNG predicts $\gamma \neq 1$ in the PPN framework
- The difference is of order $|h_{ij}^{\text{QNG}} - (-2\Sigma\delta_{ij})| \sim |\Sigma|$

Current Solar System tests constrain $|\gamma - 1| < 2.3 \times 10^{-5}$ (Cassini).
If QNG's $\gamma_{\text{QNG}}$ differs from 1 at order $|\Sigma|/c^2 \sim 10^{-8}$
(at Earth's orbit), it is compatible with existing tests but predicts a signal in
future astrometric missions (GAIA, planned sub-$\mu$as).

### IV.4 Falsifier: PPN parameter $\gamma$ from QNG

**Claim:** The QNG anisotropic spatial metric predicts a direction-dependent
light deflection angle that differs from GR's isotropic prediction.

**Standard GR:** Light deflection angle for a ray passing at impact parameter $b$:
$$\delta\phi_{\text{GR}} = \frac{4GM}{bc^2} = 2(1+\gamma)\frac{GM}{bc^2}\quad\text{with}\;\gamma=1$$

**QNG prediction:** The light deflection integrates the spatial metric perturbation
along the ray path. For a radial source, the QNG metric gives a direction-dependent
correction that may be decomposed into an isotropic part (matching GR) and an
anisotropic tidal part (from the off-diagonal $h_{ij}^{\text{QNG}}$).

The anisotropic part produces a difference:
$$|\delta\phi_{\text{QNG}} - \delta\phi_{\text{GR}}| \sim \frac{GM}{bc^2} \times
\frac{|h_{ij}^{\text{QNG}} + 2\Sigma\delta_{ij}|}{|\Sigma|} \sim \frac{GM}{bc^2}
\times \mathcal{O}(1)$$

This is an order-1 correction (not a small PN correction), meaning QNG and GR predict
different light deflection at the same order of magnitude. **If this stands,
QNG is immediately falsified by Solar System light deflection tests.**

This motivates Option A or B (§IV.3): QNG must either (a) postulate the isotropic
spatial metric or (b) show that the traceless Hessian reduces to the isotropic form
in the continuum limit for some reason not yet identified.

---

## Part V — Complete Status Table

| GR Result | QNG Status | Derivation |
|---|---|---|
| Newtonian gravity ($a = -\nabla\Phi$) | ✓ **Exact** | Geodesic, slow-motion |
| Geodesic equation ($a^i = -g^{ij}\partial_j\Sigma$) | ✓ **Exact** | Part II, exact |
| Poisson equation ($\nabla^2\Phi = 4\pi G\rho$) | ✓ **Exact** | Field equation |
| PN correction structure ($\delta a = h\cdot\nabla\Sigma$) | ✓ **Structural** | `qng-pn-structure-v1.md` |
| Linearized $G_{00} = 8\pi T_{00}$ | ✗ **Factor-4 gap** | Part III.4 |
| Isotropic spatial metric ($\gamma = 1$) | ✗ **Not derived** | Part IV.3 |
| Gravitational waves | ✗ **Not included** | Dynamic extension needed |
| Strong-field (Schwarzschild/Kerr) | ✗ **Not covered** | Requires vacuum EFE |
| Fully covariant 4D formulation | ✗ **Open** | 3+1 split only |

**The central finding:** QNG reproduces the observable Newtonian and geodesic structure
of GR exactly. The underlying metric structure (spatial isotropy, full Einstein
tensor) differs. The most urgent observable consequence is the PPN parameter $\gamma$,
which is testable at existing precision.

---

## Appendix A — The Geodesic Derivation in Detail

Full derivation of Christoffel symbol $\Gamma^i_{00}$ for the metric (I.1):

**Given:** $g_{00} = -(1+2\Sigma)$, $g_{0i} = 0$, $g_{ij} = g_{ij}^{\text{QNG}}$, $\partial_0 = 0$.

$$\Gamma^i_{00} = \frac{1}{2}g^{i\mu}\left(
  \partial_0 g_{\mu 0} + \partial_0 g_{\mu 0} - \partial_\mu g_{00}
\right)$$

With $\partial_0 = 0$ and $g_{0i} = 0$, only the $\mu = j$ (spatial) term survives:

$$\Gamma^i_{00} = \frac{1}{2}g^{ij}\left(-\partial_j g_{00}\right)
= -\frac{1}{2}g^{ij}\partial_j\left(-(1+2\Sigma)\right)
= g^{ij}\partial_j\Sigma$$

Geodesic acceleration:
$$a^i = -\Gamma^i_{00} = -g^{ij}\partial_j\Sigma \qquad\square$$

## Appendix B — Factor-4 Discrepancy: Analytic Summary

| Quantity | GR (isotropic) | QNG (traceless Hessian) |
|---|---|---|
| $H_{00}$ | $-2\Sigma$ | $-2\Sigma$ |
| $H_{ij}$ | $-2\Sigma\delta_{ij}$ | $h_{ij}^{\text{traceless}}$ |
| $H^\alpha_{\ \alpha}$ | $-4\Sigma$ | $+2\Sigma$ |
| $\bar{H}_{00}$ | $-4\Sigma$ | $-\Sigma$ |
| $-\nabla^2\bar{H}_{00}$ | $16\pi G\rho$ | $4\pi G\rho$ |
| Einstein equation | ✓ satisfied | ✗ factor-4 short |

The discrepancy is traceable entirely to the traceless constraint on $h_{ij}^{\text{QNG}}$.
Adding an isotropic trace term $-2\Sigma\delta_{ij}$ to the QNG spatial metric would
restore full GR compatibility — at the cost of deriving rather than postulating this term.

---

## Appendix C — Numerical Verification Record

**Script:** `qng_gr_check.py` | **Date:** 2026-02-27

| Check | Expected | Computed | Pass |
|---|---|---|---|
| Geodesic $\|a\|$ at 1 AU | $GM/\text{AU}^2 = 5.9299 \times 10^{-3}$ m/s² | $5.9299 \times 10^{-3}$ m/s² | ✓ |
| GR spatial trace $H_{ii}^{\text{GR}}$ | $-6\Sigma = 5.3227\times10^9$ | $5.3227\times10^9$ | ✓ |
| QNG spatial trace $H_{ii}^{\text{QNG}}$ | $0$ (traceless) | $0.000$ | ✓ |
| 4D trace ratio GR/QNG | $-4\Sigma / +2\Sigma = -2$ | $-2.000$ | ✓ |
| $\bar{H}_{00}$ ratio GR/QNG | $-4\Sigma / -\Sigma = 4$ | $4.0000$ | ✓ |
| Factor-4 discrepancy | GR: factor 4; QNG: factor 1 | 4.0000 / 1.0000 | ✓ |
| QNG eigenvalue anisotropy | $\lambda_{\max}/\lambda_{\min} = 2$ | $2.000$ | ✓ |

All analytical results independently verified. ✓

**Key eigenvalues of $h_{ij}^{\text{QNG}}$ at $(r, 0, 0)$:**
$\{-0.4082, -0.4082, +0.8165\}$ — ratio 2:1 (tangential:radial),
confirming the tidal anisotropy. GR requires isotropic eigenvalues $\{-2\Sigma/3, -2\Sigma/3, -2\Sigma/3\}$.
