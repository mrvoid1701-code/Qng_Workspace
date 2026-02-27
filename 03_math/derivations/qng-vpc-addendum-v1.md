# VPC Addendum: Coordinate Dependence and Clarification — v1

**Status:** Critical clarification — VPC is coordinate-sensitive
**Date:** 2026-02-27
**Depends on:** `qng-vpc-derivation-v1.md` (which this addendum extends)
**Test script:** `qng_vpc_test_v2.py`

---

## 1. What the numerical test found

The full Hessian lag formula $a^i_{\text{lag}} = -\tau\, v^j\, H_{ij}$ was tested
numerically at a test point $(r, 0, 0)$ with radial and tangential velocities
in the Kepler field $\Sigma = -GM/r$. Two versions of $H_{ij}$ were computed:

### 1.1 Cartesian Hessian

At $(r, 0, 0)$: the Cartesian Hessian is diagonal with entries

$$H^{\text{Cart}}_{xx} = -\frac{2GM}{r^3}, \quad
H^{\text{Cart}}_{yy} = H^{\text{Cart}}_{zz} = +\frac{GM}{r^3}$$

**Result for tangential velocity $\mathbf{v} = (0, v, 0)$:**

$$a^y_{\text{lag}} = -\tau\, v\, H^{\text{Cart}}_{yy} = -\frac{\tau\, GM\, v}{r^3} \neq 0$$

The tangential lag is **non-zero** and equals exactly $\tfrac{1}{2}$ the radial lag
at all distances. This is a *constant* ratio, not a small correction:

$$\frac{|a^{\perp}_{\text{lag}}|}{|a^r_{\text{lag}}|} = \frac{H_{yy}}{|H_{xx}|}
= \frac{1}{2} \quad \text{(exact, all } r\text{)}$$

### 1.2 Spherical Hessian

In spherical coordinates $\Sigma = -GM/r$ is independent of $\theta$ and $\phi$.
The second partial derivatives:

$$\frac{\partial^2 \Sigma}{\partial \theta^2} = 0, \qquad
\frac{\partial^2 \Sigma}{\partial \phi^2} = 0, \qquad
\frac{\partial^2 \Sigma}{\partial r^2} = -\frac{2GM}{r^3}$$

**Result for any tangential velocity component:**

$$a^{\theta}_{\text{lag}} = -\tau\, v^{\theta}\, H^{\text{sph}}_{\theta\theta} = 0
\quad \text{(exact)}$$
$$a^{\phi}_{\text{lag}} = -\tau\, v^{\phi}\, H^{\text{sph}}_{\phi\phi} = 0
\quad \text{(exact)}$$

**VPC holds exactly** when the Hessian is computed in spherical coordinates.

---

## 2. Why the Cartesian result is not physically wrong — it's a different formula

The Cartesian formula $-\tau v^j H^{\text{Cart}}_{ij}$ and the spherical formula
$-\tau v^j H^{\text{sph}}_{ij}$ compute *different things*, both of which can be
legitimate QNG lag formulas depending on the graph structure:

**Cartesian-grid graph:** nodes arranged in a Cartesian lattice. The natural
Hessian for this graph uses finite differences along $x, y, z$. This gives
$H^{\text{Cart}}_{yy} \neq 0$ and hence nonzero tangential lag.

**Spherically-symmetric graph:** nodes distributed uniformly on shells of
constant $r$. The natural Hessian involves differences along $r$ only (since
$\Sigma$ is constant on each shell). This gives $H^{\text{sph}}_{\theta\theta} = 0$
and hence zero tangential lag — VPC holds.

**The QNG claim:** the physical vacuum is assumed to have a graph that respects
the symmetries of the dominant field. In a spherically-symmetric field, this
means a spherically-symmetric graph, and VPC follows.

This is *stronger* than assumption (A1) of `qng-vpc-derivation-v1.md`: it requires
not just that $\Sigma$ is spherically symmetric, but that the **graph itself** is
spherically symmetric (or at least that the lag is computed using the symmetry-adapted
Hessian).

---

## 3. Revised VPC statement

**VPC (revised):** In a QNG graph with spherically-symmetric node distribution
embedded in a spherically-symmetric field $\Sigma = \Sigma(r)$, the lag acceleration
computed from the symmetry-adapted Hessian $H^{\text{sph}}_{ij}$ reduces to
the purely radial form:

$$a^i_{\text{lag}} = -\tau_{\text{phys}}\, v_r\, \frac{d^2\Sigma}{dr^2}\, \hat{r}^i$$

Equivalently, this can be written as:

$$a^i_{\text{lag}} = -\tau_{\text{phys}}\, (v^j \nabla_j)(\nabla^i\Sigma)\Big|_{\text{radial projection}}$$

where "radial projection" means only the component along $\hat{r}$ is retained.

---

## 4. Practical implication for QNG simulations

Any numerical implementation using a **Cartesian grid** will automatically
generate a spurious tangential lag equal to 50% of the radial lag. This would:

1. Produce secular angular drift in bound orbits (slowly changing eccentricity)
2. Generate an anomalous precession rate $\dot{\omega} \sim \tau \,GM\, v/r^3$
3. Violate observed orbital stability of Solar System planets

**Fix:** Either (a) use spherical coordinates in the QNG graph simulation,
or (b) explicitly project $H_{ij}$ onto the gradient direction:

$$H^{\text{VPC}}_{ij} = \hat{r}_i\, H_{kl}\, \hat{r}^k\, \hat{r}^l\, \hat{r}_j$$

Option (b) can be applied post-hoc in Cartesian code and is computationally
straightforward.

---

## 5. Falsifier

The tangential contamination in a Cartesian-grid QNG simulation predicts
anomalous precession of circular orbits at rate:

$$\Delta\omega_{\text{lag}} \sim \frac{\tau\, GM}{r^3\, T_{\text{orbit}}}
\sim 10^{-18} \text{ rad/s} \quad \text{at Earth orbit}$$

This is below current VLBI/laser-ranging precision ($\sim 10^{-15}$ rad/s for
planetary perihelion shifts). However, for tight pulsar binaries where
$\tau_{\text{phys}}$ could be much larger (if the straton scale is different in
strong gravity), this could provide a constraint.

---

## 6. Summary of VPC status (updated)

| Context | VPC status | Basis |
|---|---|---|
| Spherically symmetric graph, sph. coords | **Exact** | $\partial^2\Sigma/\partial\theta^2 = 0$ identically |
| Spherically symmetric graph, Cartesian formula | **Fails** | $H^{\text{Cart}}_{yy} = GM/r^3 \neq 0$ |
| Asymmetric field (general $\Sigma$) | **Approximate** | O($l_0/r$) corrections from non-spherical terms |
| QNG simulation on Cartesian grid | **Manual fix needed** | Project $H_{ij}$ onto gradient direction |

The VPC derivation in `qng-vpc-derivation-v1.md` (§2, §3) is correct but
implicitly assumes the spherical-coordinates Hessian. This addendum makes that
assumption explicit and provides the coordinate-invariant formulation.
