# QNG Straton Interpretation of τ — v1

**Status:** Theoretical hypothesis
**Date:** 2026-02-26
**Depends on:** T-028 fit (τ_graph = 0.002051), Pioneer anomaly data, qng-tau-physical-interpretation-v1

---

## 1. Motivation

The QNG acceleration law contains a lag term:

$$
a^i_{\text{lag}} = -\tau \, v^j \, \partial_j \partial_i \Sigma
$$

where $\Sigma$ is the stability field (units: m²/s²) and $\tau$ has units of time.
The numerical fit from T-028 gives $\tau_{\text{graph}} = 0.002051$, which is
dimensionless — it counts update steps, not seconds.

**Problem:** How does τ_graph connect to physical time?

---

## 2. The Straton Framework

### 2.1 Definition

One **straton** ($t_s$) is the fundamental time unit of the QNG discrete spacetime:
the time required for information to propagate across one graph edge.

$$
t_s = \frac{l_0}{c}
$$

where $l_0$ is the physical lattice scale (graph edge length) and $c$ is the
speed of light.

### 2.2 Physical lag time

The physical relaxation time is:

$$
\tau_{\text{phys}} = \tau_{\text{graph}} \cdot t_s
$$

**Interpretation:** The spacetime network does not react instantaneously.
After an object passes through a region, the local geometry relaxes over
$\tau_{\text{graph}}$ update cycles, each lasting $t_s$ seconds.
Therefore $\tau$ is emergent, not fundamental.

### 2.3 Velocity-projection coupling

From the Hessian of $\Sigma = -GM/r$, the full lag term decomposes as:

$$
a^r_{\text{lag}} = -2\tau \frac{GM}{r^3} v_r
\qquad
a^\theta_{\text{lag}} = +\tau \frac{GM}{r^3} v_\theta
$$

The tangential component ($\propto v_\theta$) would produce secular energy
changes for bound orbits. We adopt the **velocity-projection coupling**:
only the radial velocity component $v_r$ enters the lag.

Physical justification: the lag arises from the object traversing new graph
nodes. For circular motion, the object revisits the same geometric region —
no new relaxation is triggered. Only radial penetration into fresh geometry
activates the lag.

**Working formula:**

$$
\boxed{a_{\text{lag}} = -2\,\tau_{\text{phys}}(r)\,v_r\,\frac{GM}{r^3}\,\hat{r}}
$$

---

## 3. Scenario A — Constant Straton

### 3.1 Setup

Assume $t_s = \text{const}$ everywhere. Then $\tau_{\text{phys}} = 0.002051 \times t_s$.

$$
a_{\text{lag}}(r) = \frac{2\,\tau_{\text{graph}}\,t_s\,v_r\,GM}{r^3}
$$

This scales as $r^{-3}$ for fixed $v_r$.

### 3.2 Pioneer calibration

At $r = 40\,\text{AU}$, $v_r = 12.5\,\text{km/s}$, requiring
$a_P = 8.74 \times 10^{-10}\,\text{m/s}^2$:

$$
t_s = \frac{a_P \, r^3}{2\,\tau_{\text{graph}}\,v_r\,GM_\odot}
= 2.75 \times 10^7\,\text{s} \approx 318\,\text{days}
$$

$$
l_0 = c \cdot t_s = 8.25 \times 10^{15}\,\text{m} \approx 55\,000\,\text{AU}
\approx 0.87\,\text{ly}
$$

### 3.3 Failure diagnosis

| Distance | $a_{\text{lag}}$ | Ratio to $a_P$ |
|----------|------------------:|:----------------|
| 20 AU    | $7.0 \times 10^{-9}$ | 8.0× too large |
| 40 AU    | $8.7 \times 10^{-10}$ | 1.0× (calibrated) |
| 70 AU    | $1.6 \times 10^{-10}$ | 0.19× too small |

The observed Pioneer anomaly is approximately constant from 20 to 70 AU.
A $1/r^3$ profile varies by a factor 42× across this range.

At Mercury ($r = 0.387\,\text{AU}$), even with velocity-projection coupling:
$a_{\text{lag,max}} = 7.6 \times 10^{-4}\,\text{m/s}^2$, which is 1.9% of
the Newtonian acceleration — catastrophically excluded.

**Verdict:** Scenario A is ruled out.

---

## 4. Scenario B — Field-Dependent Straton

### 4.1 Hypothesis

The lattice scale depends on the local gravitational field strength:

$$
l_0(r) = l_{0,\text{ref}} \left(\frac{|\nabla\Sigma_{\text{ref}}|}{|\nabla\Sigma(r)|}\right)^\alpha
$$

Since $|\nabla\Sigma| = GM/r^2$, this gives:

$$
l_0(r) = l_{0,\text{ref}} \left(\frac{r}{r_{\text{ref}}}\right)^{2\alpha}
\qquad
t_s(r) = t_{s,\text{ref}} \left(\frac{r}{r_{\text{ref}}}\right)^{2\alpha}
$$

Substituting into the lag formula:

$$
a_{\text{lag}} \propto r^{2\alpha} \cdot r^{-3} = r^{2\alpha - 3}
$$

### 4.2 Critical exponent

For a **distance-independent** anomaly (constant $a_{\text{lag}}$ for constant $v_r$):

$$
2\alpha - 3 = 0 \quad\Longrightarrow\quad \boxed{\alpha = \frac{3}{2}}
$$

This gives:

$$
t_s(r) = t_{s,\text{1AU}} \left(\frac{r}{1\,\text{AU}}\right)^3
\qquad
l_0(r) = l_{0,\text{1AU}} \left(\frac{r}{1\,\text{AU}}\right)^3
$$

### 4.3 Calibration

With $\alpha = 3/2$, the lag acceleration becomes exactly r-independent:

$$
a_{\text{lag}} = \frac{2\,\tau_{\text{graph}}\,t_{s,\text{1AU}}\,GM_\odot}{(1\,\text{AU})^3} \cdot v_r
= C \cdot v_r
$$

From Pioneer: $C = a_P / v_{r,P} = 6.99 \times 10^{-14}\,\text{s}^{-1}$.

Solving for the reference straton:

$$
t_{s,\text{1AU}} = \frac{C \cdot (1\,\text{AU})^3}{2\,\tau_{\text{graph}}\,GM_\odot}
= 430\,\text{s} \approx 7.2\,\text{min}
$$

$$
l_{0,\text{1AU}} = c \cdot t_{s,\text{1AU}} = 1.29 \times 10^{11}\,\text{m}
\approx 0.86\,\text{AU}
$$

### 4.4 Lattice scale across the solar system

| Location | $r$ (AU) | $l_0$ | $t_s$ |
|----------|:--------:|------:|------:|
| Mercury  | 0.387    | 0.050 AU | 25 s |
| Earth    | 1.0      | 0.86 AU | 7.2 min |
| Jupiter  | 5.2      | 121 AU | 16.8 hr |
| Pioneer (40 AU) | 40 | 55,200 AU (0.87 ly) | 318 days |
| Oort cloud | 100  | 862,000 AU (13.6 ly) | 13.6 yr |

**Physical picture:** The QNG graph is dense near massive objects (small $l_0$)
and sparse in deep space (large $l_0$). This mirrors the idea that spacetime
geometry is "resolved" more finely where curvature is stronger.

### 4.5 Mercury constraint — PASSED

With $\alpha = 3/2$ and velocity-projection coupling:

- $\tau_{\text{phys}}(\text{Mercury}) = 0.051\,\text{s}$
- Maximum instantaneous $a_{\text{lag}} = C \times v_{r,\text{max}} = 6.88 \times 10^{-10}\,\text{m/s}^2$
- Fraction of Newtonian: $1.7 \times 10^{-8}$ (17 ppb)
- **Secular average over orbit: exactly zero** (v_r changes sign symmetrically)
- Perihelion advance effect: zero to first order

Mercury is safe by a wide margin.

### 4.6 All planetary constraints — PASSED

For any bound orbit with eccentricity $e$:

1. $v_r$ oscillates with zero mean over one period
2. $a_{\text{lag}} = C \cdot v_r$ therefore averages to zero
3. No secular change in semi-major axis, eccentricity, or perihelion
4. Maximum instantaneous fraction of Newtonian acceleration:
   at most $\sim 10^{-7}$ (Saturn), well below current measurement precision

### 4.7 Verification: constant anomaly across all r

By construction, $a_{\text{lag}} = C \cdot v_r$ with no r-dependence.
Numerical verification confirms $a_{\text{lag}} = 8.74 \times 10^{-10}\,\text{m/s}^2$
identically at $r = 0.387, 1, 5.2, 20, 40, 70, 100\,\text{AU}$
for $v_r = 12.5\,\text{km/s}$.

---

## 5. Testable Predictions

The model predicts: $a_{\text{anomaly}} = C \cdot v_r$ with $C = 6.99 \times 10^{-14}\,\text{s}^{-1}$.

| Probe | $v_r$ (km/s) | Predicted $a$ (m/s²) |
|-------|:------------:|:--------------------:|
| Pioneer 10 | 12.5 | $8.74 \times 10^{-10}$ (calibrated) |
| Pioneer 11 | 11.6 | $8.11 \times 10^{-10}$ |
| Voyager 1 | 17.0 | $1.19 \times 10^{-9}$ |
| Voyager 2 | 15.4 | $1.08 \times 10^{-9}$ |
| New Horizons | 14.5 | $1.01 \times 10^{-9}$ |

**Key prediction:** The anomaly scales linearly with $v_r$, NOT constant
across probes with different velocities. Voyager 1 should show ~36% larger
anomaly than Pioneer 10. This is a sharp, falsifiable prediction.

**Note:** The conventional explanation (thermal recoil) predicts an anomaly
that decreases over time as RTG power decays. The QNG prediction depends
on $v_r$, not RTG power. These are distinguishable in principle.

---

## 6. Free Parameter Count

| Parameter | Value | Status |
|-----------|-------|--------|
| $\tau_{\text{graph}}$ | 0.002051 | Fitted from T-028 (graph simulations) |
| $\alpha$ | 3/2 | Fixed by requiring constant Pioneer anomaly |
| $t_{s,\text{1AU}}$ | 430 s | Calibrated from Pioneer magnitude |

**Total free parameters introduced: 1** ($t_{s,\text{1AU}}$, or equivalently $l_{0,\text{1AU}}$).

The exponent $\alpha = 3/2$ is not free — it is uniquely determined by the
requirement that the anomaly be distance-independent.

---

## 7. Physical Interpretation of the Straton

### 7.1 Three candidate interpretations

**A. Relaxation time of discrete geometry.**
After a mass perturbs the local graph, the nodes rearrange over $\tau_{\text{graph}}$
update steps. Each step takes $t_s$ seconds. The graph is "stiff" in strong
fields (small $t_s$, fast relaxation) and "soft" in weak fields (large $t_s$,
slow relaxation).

**B. Information propagation time.**
$t_s = l_0/c$ is literally the light-crossing time of one graph edge.
The lag arises because geometric information propagates at finite speed $c$
across the discrete structure. In dense regions (small $l_0$), updates
propagate quickly; in sparse regions (large $l_0$), slowly.

**C. Stability-selection timescale.**
The Σ dynamics equation $\partial_i(g^{ij}\partial_j\Sigma) = 4\pi\rho$
has a characteristic relaxation rate set by the eigenvalues of the
variable-coefficient operator. In regions of strong curvature, the
operator has large eigenvalues (fast relaxation); in flat regions,
small eigenvalues (slow relaxation).

### 7.2 Assessment

Interpretation **B** (information propagation) is the most parsimonious:
it introduces no new concept beyond the graph structure itself.
The scaling $l_0 \propto |\nabla\Sigma|^{-3/2}$ then says: the graph is
denser where the field gradient is stronger. This is physically natural —
more geometric structure is needed to encode stronger curvature.

Interpretation **A** is equivalent to **B** if the update mechanism is
causal (limited by $c$). Interpretation **C** requires solving the full
Σ operator spectrum, which is future work.

**Recommended interpretation:** B, with A as the macroscopic consequence.

---

## 8. The Scaling $l_0 \propto |\nabla\Sigma|^{-3/2}$

### 8.1 Dimensional analysis

$$
l_0 = l_{0,\text{ref}} \left(\frac{|\nabla\Sigma|}{|\nabla\Sigma_{\text{ref}}|}\right)^{-3/2}
$$

Since $|\nabla\Sigma| = GM/r^2$ has units of m/s², this can be written:

$$
l_0 = \lambda_0 \cdot \left(\frac{a_0}{|\nabla\Sigma|}\right)^{3/2}
$$

where $a_0$ is a reference acceleration and $\lambda_0$ a reference length.
From Pioneer calibration:

$$
a_0 \equiv \frac{GM_\odot}{(1\,\text{AU})^2} = 5.93 \times 10^{-3}\,\text{m/s}^2
$$

$$
\lambda_0 = l_{0,\text{1AU}} = 0.86\,\text{AU}
$$

### 8.2 Suggestive connection to MOND

The MOND acceleration scale is $a_{\text{MOND}} \approx 1.2 \times 10^{-10}\,\text{m/s}^2$.
In QNG, the transition to "large $l_0$" (sparse graph) occurs where the lag
term becomes comparable to Newtonian acceleration:

$$
|\nabla\Sigma| \sim a_{\text{MOND}} \quad\Longrightarrow\quad
l_0 \sim \lambda_0 \left(\frac{a_0}{a_{\text{MOND}}}\right)^{3/2}
\approx 0.86 \times (4.94 \times 10^7)^{3/2}
\approx 9.5 \times 10^{11}\,\text{AU}
$$

This corresponds to $r \approx 10^4\,\text{AU}$, which is the scale where
QNG effects become dominant. A possible future direction: derive the MOND
interpolating function from QNG graph density.

---

## 9. Connection to Quantum Regime

### 9.1 Planck scale

The lattice scale reaches the Planck length $l_P = 1.6 \times 10^{-35}\,\text{m}$
at a distance from a solar-mass object:

$$
r_{\text{Planck}} = 1\,\text{AU} \times \left(\frac{l_P}{l_{0,\text{1AU}}}\right)^{1/3}
\approx 7.5 \times 10^{-5}\,\text{m}
$$

This is deep inside the Schwarzschild radius ($r_S = 3\,\text{km}$ for the Sun),
so the Planck regime occurs only inside black holes. The QNG graph becomes
a continuum ($l_0 \to 0$) in the strong-field limit, recovering smooth GR.

### 9.2 Dispersion relations

If the graph has a minimum edge length $l_{\min}$, then wavelengths shorter
than $l_{\min}$ cannot propagate. This would produce a UV cutoff in the
propagator for Σ fluctuations:

$$
k_{\max}(r) = \frac{2\pi}{l_0(r)}
$$

In the inner solar system ($l_0 \sim 10^{11}\,\text{m}$), this cutoff is at
macroscopic scales — no quantum gravity effects are visible.
In the extreme strong field ($l_0 \to l_P$), the cutoff approaches the
Planck energy, potentially connecting to quantum gravity.

### 9.3 Stability quantization

If Σ is quantized on the graph (discrete node values), then the energy
spectrum of the $\partial_i(g^{ij}\partial_j\Sigma)$ operator would be discrete.
The straton $t_s$ is then the inverse of the largest eigenvalue — the
fastest mode of the graph. This is speculative but would provide a
principled derivation of $t_s$ from first principles.

---

## 10. Summary of Results

### What works

1. **Scenario B** ($\alpha = 3/2$) produces a **constant** Pioneer anomaly
   across all distances, with only **one free parameter** ($t_{s,\text{1AU}} = 430\,\text{s}$).

2. **Velocity-projection coupling** ensures all bound orbits have
   **zero secular lag effect**, satisfying Mercury and all planetary constraints.

3. The lattice scale $l_0 \propto r^3$ gives a physically natural picture:
   dense graph near masses, sparse graph in deep space.

4. **Falsifiable prediction:** anomaly $\propto v_r$, so Voyager 1
   should show 36% larger anomaly than Pioneer 10.

### What remains open

1. The exponent $\alpha = 3/2$ is phenomenologically determined, not derived
   from the QNG field equations. **Next step:** derive $l_0(\Sigma)$ from the
   Σ dynamics equation or from a graph-theoretic argument.

2. The velocity-projection coupling is imposed, not emergent. **Next step:**
   show that the full Hessian lag term reduces to the $v_r$-only form when
   integrated over the graph averaging kernel.

3. The value $l_{0,\text{1AU}} = 0.86\,\text{AU}$ is calibrated, not predicted.
   **Next step:** relate $l_{0,\text{1AU}}$ to a fundamental QNG parameter
   (e.g., node density, coupling constant).

### Recommended next theoretical step

Derive the scaling $l_0 \propto |\nabla\Sigma|^{-3/2}$ from the
condition that the graph Laplacian eigenspectrum is self-similar
across scales. If the graph operator $\partial_i(g^{ij}\partial_j)$
must have a scale-invariant smallest eigenvalue when expressed in
units of $l_0$, this may uniquely fix $\alpha = 3/2$.

---

## Appendix: Complete Formula

The QNG lag acceleration in the straton framework is:

$$
\boxed{
a^i_{\text{lag}} = -\frac{2\,\tau_{\text{graph}}\,l_{0,\text{ref}}}{c\,r_{\text{ref}}^3}
\cdot v_r \cdot \frac{GM}{1} \cdot \hat{r}^i
}
$$

where the entire bracket is a **universal constant** $C = 6.99 \times 10^{-14}\,\text{s}^{-1}$,
and the anomaly is simply:

$$
a_{\text{anomaly}} = C \cdot v_r
$$

with $C$ determined by a single calibration (Pioneer 10).
