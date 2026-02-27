# Velocity-Projection Coupling: Derivation from Graph Symmetry — v1

**Status:** Partial derivation (valid under stated assumptions)
**Date:** 2026-02-27
**Depends on:** qng-straton-interpretation-v2.md (§ 9.4)

---

## 1. Statement

**Theorem (conditional).** *In a QNG graph with statistically isotropic node
distribution embedded in a spherically symmetric stability field
$\Sigma = \Sigma(r)$, the discrete lag term reduces to the radial-velocity
form (Eq. 2 of straton v2) in the continuum limit. The tangential component
vanishes identically.*

**Assumptions required:**

- (A1) The background field is spherically symmetric: $\Sigma = \Sigma(r)$.
- (A2) The QNG graph node distribution is statistically isotropic (no
  preferred angular direction at fixed $r$).
- (A3) The emergent metric $g_{ij}$ depends only on $r$ and on the local
  graph structure (not on angular position).

---

## 2. Physical argument

### 2.1 What generates the lag

The lag term arises because the spacetime graph takes time $\tau_{\text{phys}}$
to relax after an object passes through a region. During this time, the object
has moved a displacement $\delta\mathbf{x} = \mathbf{v} \cdot \tau_{\text{phys}}$,
and the local metric it experiences is the "old" metric from its previous
position, not the "correct" metric at its new position.

The lag acceleration is proportional to the **metric mismatch**:

$$\Delta g_{ij} \equiv g_{ij}(\mathbf{x}_{\text{old}}) - g_{ij}(\mathbf{x}_{\text{new}})
\approx -\delta x^k \,\partial_k g_{ij} \tag{1}$$

### 2.2 Tangential displacement in a spherically symmetric field

Decompose the displacement into radial and tangential components:

$$\delta\mathbf{x} = \delta x_r \,\hat{r} + \delta\mathbf{x}_\perp$$

where $\delta x_r = v_r \,\tau_{\text{phys}}$ and
$\delta\mathbf{x}_\perp = \mathbf{v}_\perp \,\tau_{\text{phys}}$.

**Key observation:** Under assumption (A1), the metric $g_{ij}$ depends only
on $r$. A tangential displacement $\delta\mathbf{x}_\perp$ maps the object to
a new angular position at the **same radius**. By spherical symmetry:

$$g_{ij}(r, \theta + \delta\theta, \phi + \delta\phi) = g_{ij}(r, \theta, \phi)
\tag{2}$$

Therefore the metric mismatch from the tangential displacement vanishes:

$$\delta x_\perp^k \,\partial_k g_{ij} = 0 \tag{3}$$

Only the radial displacement contributes:

$$\Delta g_{ij} = -v_r \,\tau_{\text{phys}} \,\partial_r g_{ij} \tag{4}$$

### 2.3 Consequence for the lag acceleration

The lag acceleration is driven by the metric mismatch. Since $\Delta g_{ij}$
is proportional to $v_r$ only (Eq. 4), the resulting acceleration depends only
on $v_r$:

$$a^i_{\text{lag}} \propto v_r \times (\text{radial gradient of metric})$$

For $\Sigma = -GM/r$ with flat background metric, expanding the Hessian terms:

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \cdot v_r \cdot \partial_r(g^{ik}\partial_k\Sigma)$$

The tangential velocity $v_\theta$ does **not** appear. This is VPC.

---

## 3. Formal derivation on the discrete graph

### 3.1 Setup

Consider a QNG graph $\mathcal{G} = (V, E)$ with nodes $\{x_n\}$ distributed
in $\mathbb{R}^3$. At each node, the emergent metric is computed from the local
Hessian of $\Sigma$ over neighboring nodes (metric hardening v4 procedure).

An object at node $x_A$ at time $t$ experiences the metric $g_{ij}(x_A, t)$.
At time $t + \tau_{\text{phys}}$, it has moved to position $x_B$. Due to the
lag, it still experiences the old metric $g_{ij}(x_A, t)$ instead of the
correct metric $g_{ij}(x_B, t + \tau_{\text{phys}})$.

### 3.2 Graph averaging over angular neighbors

At fixed radius $r$, the set of graph nodes within angular distance $\delta\theta$
forms a spherical shell patch. By assumption (A2), these nodes are distributed
isotropically.

The emergent metric at any node in this shell depends on $r$ and on the local
node configuration. Averaging over the angular distribution of neighbors:

$$\langle g_{ij}(r, \Omega) \rangle_\Omega = \bar{g}_{ij}(r) \tag{5}$$

where $\bar{g}_{ij}(r)$ is a function of $r$ only.

### 3.3 Cancellation of tangential lag

For tangential motion $x_A \to x_B$ at fixed $r$, nodes $x_A$ and $x_B$ are
both at radius $r$ but at different angles. By Eq. (5):

$$\langle g_{ij}(x_B) \rangle = \langle g_{ij}(x_A) \rangle = \bar{g}_{ij}(r)$$

The **expected** metric mismatch from tangential motion is:

$$\langle \Delta g_{ij} \rangle_{\text{tangential}} = \bar{g}_{ij}(r) - \bar{g}_{ij}(r) = 0 \tag{6}$$

The tangential lag vanishes on average. Individual realizations of the graph
will have $O(1/\sqrt{N_{\text{neighbors}}})$ fluctuations, but these are
noise, not a systematic lag.

### 3.4 Survival of radial lag

For radial motion $x_A \to x_C$ where $x_C$ is at radius $r + \delta r$:

$$\langle \Delta g_{ij} \rangle_{\text{radial}} = \bar{g}_{ij}(r) - \bar{g}_{ij}(r + \delta r)
= -\delta r \,\partial_r \bar{g}_{ij} \neq 0 \tag{7}$$

The radial lag survives because $\bar{g}_{ij}$ genuinely varies with $r$.

---

## 4. Generalization beyond spherical symmetry

For a general (non-spherically-symmetric) field $\Sigma(\mathbf{x})$, the
argument generalizes to:

**VPC (general form).** *The lag term couples to the component of velocity
along the gradient of $\Sigma$:*

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \cdot (\mathbf{v} \cdot \hat{\nabla}\Sigma)
\cdot \hat{\nabla}\Sigma^j \cdot \partial_j(g^{ik}\partial_k\Sigma) \tag{8}$$

**Justification:** The metric mismatch is driven by changes in $|\nabla\Sigma|$
along the trajectory. Motion along equipotential surfaces
($\mathbf{v} \perp \nabla\Sigma$) does not change the local field strength,
so the metric encountered at the new position matches the old metric.

This generalization requires:

- (A1') $g_{ij}$ is determined primarily by $|\nabla\Sigma|$ (the emergent
  metric depends on field strength, not on position per se).
- (A2') The graph is locally isotropic in the tangent plane perpendicular to
  $\nabla\Sigma$.

### 4.1 Where the generalization breaks down

In regions where $\nabla\Sigma$ changes direction rapidly (e.g., near the
saddle point between two masses), the equipotential surfaces are not locally
flat, and the tangential cancellation may be incomplete. The correction is of
order:

$$\delta a_{\text{tang}} \sim \tau_{\text{phys}} \cdot v_\perp \cdot
|\nabla\Sigma| \cdot \kappa \cdot l_0 \tag{9}$$

where $\kappa$ is the curvature of the equipotential surface. For the
solar system (single dominant mass), $\kappa \sim 1/r$ and this correction is
suppressed by $l_0/r \ll 1$.

---

## 5. Status summary

| Claim | Status |
|-------|--------|
| VPC holds for spherically symmetric $\Sigma$ | **Derived** (under A1–A3) |
| VPC holds for general central-field solar system | **Derived** (under A1'–A2', with $O(l_0/r)$ corrections) |
| VPC holds for arbitrary $\Sigma$ (binary systems, cosmological fields) | **Not derived** (requires separate analysis) |
| Tangential lag = 0 exactly for circular orbits in central field | **Derived** |
| Tangential lag averages to 0 for eccentric orbits in central field | **Derived** ($\langle v_r \rangle = 0$ over one period) |
| VPC emerges from QNG update rule without symmetry assumptions | **Not derived** (open problem) |

**Assessment:** VPC is promoted from a bare postulate to a **derived consequence
of spherical symmetry**. In the solar system, this is an excellent approximation.
For non-spherical environments (binaries, galaxy clusters), VPC requires separate
justification.
