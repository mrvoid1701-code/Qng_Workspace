# Derivation of α = 3/2: Partial Results and Gap Analysis — v1

**Status:** Partial derivation — natural arguments give α = 3/4; gap to α = 3/2 identified
**Date:** 2026-02-27
**Depends on:** qng-straton-interpretation-v2.md (§ 7.2)

---

## 1. The problem

The field-dependent straton hypothesis is:

$$l_0(r) = l_{0,\text{ref}} \left(\frac{|\nabla\Sigma_{\text{ref}}|}{|\nabla\Sigma(r)|}\right)^\alpha$$

The Pioneer anomaly requires $\alpha = 3/2$ to produce a distance-independent
lag acceleration. The question: can $\alpha = 3/2$ be derived from QNG
principles, or is it purely phenomenological?

---

## 2. Self-similarity of the Hessian → α = 3/4

### 2.1 Setup

The tidal tensor (Hessian of $\Sigma$) has eigenvalues:

$$|H| \sim \frac{GM}{r^3}$$

On the discrete graph, the Hessian is computed from finite differences across
edges of length $l_0$. The **dimensionless curvature per graph cell** is:

$$\xi(r) \equiv |H(r)| \cdot l_0(r)^2 = \frac{GM}{r^3} \cdot l_0(r)^2 \tag{1}$$

This measures the tidal distortion across one edge — the "amount of curvature"
each graph cell must encode.

### 2.2 Self-similarity condition

**Hypothesis (H1).** *The QNG graph is self-similar: each graph cell encodes
the same dimensionless amount of curvature, regardless of position.*

$$\xi(r) = \text{const} \tag{2}$$

### 2.3 Result

From Eqs. (1)–(2):

$$\frac{GM}{r^3} \cdot l_0^2 = \text{const} \quad\Longrightarrow\quad
l_0 \propto r^{3/2} \tag{3}$$

Since $l_0 \propto |\nabla\Sigma|^{-\alpha}$ and $|\nabla\Sigma| = GM/r^2$:

$$l_0 \propto r^{2\alpha} = r^{3/2} \quad\Longrightarrow\quad
\boxed{\alpha_{\text{H1}} = \frac{3}{4}} \tag{4}$$

### 2.4 What α = 3/4 gives

With $\alpha = 3/4$, the lag acceleration scales as:

$$a_{\text{lag}} \propto r^{2\alpha - 3} = r^{-3/2} \tag{5}$$

| $r$ (AU) | $a_{\text{lag}}$ ratio to 40 AU |
|:--------:|:-------------------------------:|
| 20 | $2.83\times$ |
| 40 | $1.00\times$ (cal.) |
| 70 | $0.43\times$ |

This is a **significant improvement** over Scenario A ($r^{-3}$, which gives
$8\times$ variation), but still not distance-independent.

Across 20–70 AU, the variation is $2.83/0.43 = 6.6\times$ (vs. $42\times$
for Scenario A). Not flat enough to match Pioneer.

---

## 3. Alternative arguments and their exponents

### 3.1 Radial resolution (constant fractional metric error)

**Condition:** The fractional error in the metric across one edge is constant:

$$\frac{|\partial_r g_{ij}| \cdot l_0}{|g_{ij}|} = \text{const} \tag{6}$$

For $g_{ij} \sim 1 + O(\Sigma)$ and $|\partial_r g| \sim 1/r$ in the weak-field
limit:

$$l_0 / r = \text{const} \quad\Longrightarrow\quad l_0 \propto r
\quad\Longrightarrow\quad \alpha = \frac{1}{2} \tag{7}$$

This gives $a_{\text{lag}} \propto r^{-2}$ — worse than H1, but much better
than Scenario A.

### 3.2 Node count per orbit (dynamical resolution)

**Condition:** The number of graph updates per Keplerian orbital period is
constant:

$$\frac{T_{\text{orbit}}}{t_s} = \text{const} \tag{8}$$

Since $T_{\text{orbit}} \propto r^{3/2}$ (Kepler) and $t_s = l_0/c$:

$$l_0 \propto r^{3/2} \quad\Longrightarrow\quad \alpha = \frac{3}{4} \tag{9}$$

Same as H1. This is not a coincidence: both conditions require the graph to
"resolve" the same gravitational physics at the same level across all radii.

### 3.3 Summary of natural exponents

| Condition | α | $a_{\text{lag}}$ scaling | Variation 20–70 AU |
|-----------|:---:|:---:|:---:|
| Constant $t_s$ (Scenario A) | — | $r^{-3}$ | $42\times$ |
| Radial resolution (§3.1) | 1/2 | $r^{-2}$ | $12.3\times$ |
| Hessian self-similarity (§2) | 3/4 | $r^{-3/2}$ | $6.6\times$ |
| **Pioneer requirement** | **3/2** | **$r^0$** | **$1\times$** |

---

## 4. The gap: from α = 3/4 to α = 3/2

### 4.1 What is missing

The natural self-similarity argument gives $\alpha = 3/4$. Pioneer requires
$\alpha = 3/2$, which is exactly **twice** the self-similar value:

$$\alpha_{\text{Pioneer}} = 2 \times \alpha_{\text{H1}} \tag{10}$$

This suggests an additional factor of $l_0 \propto r^{3/2}$ beyond self-similarity
— i.e., a **squared** version of the Hessian condition.

### 4.2 Possible origin: lag coherence length

The lag produces an acceleration mismatch over a displacement
$\delta r = v_r \cdot \tau_{\text{phys}}$. The physical coherence length of
the lag is:

$$\ell_{\text{coh}} = v_r \cdot \tau_{\text{phys}} = v_r \cdot \tau_{\text{graph}} \cdot \frac{l_0}{c}
\tag{11}$$

For the lag to be **self-consistently resolved on the graph**, the coherence
length must satisfy:

$$|H| \cdot \ell_{\text{coh}}^2 = \text{const} \tag{12}$$

(same self-similarity condition as Eq. 2, but applied to $\ell_{\text{coh}}$
instead of $l_0$).

Substituting Eq. (11):

$$\frac{GM}{r^3} \cdot v_r^2 \cdot \tau_{\text{graph}}^2 \cdot \frac{l_0^2}{c^2} = \text{const}
\tag{13}$$

Since $v_r = \text{const}$ for Pioneer, and $\tau_{\text{graph}}, c$ are constants:

$$\frac{GM}{r^3} \cdot l_0^2 = \text{const} \quad\Longrightarrow\quad
l_0 \propto r^{3/2} \tag{14}$$

This is still $\alpha = 3/4$. The coherence condition doesn't add a new factor
because $v_r$ is constant.

### 4.3 Possible origin: double self-similarity

**Hypothesis (H2).** *The QNG graph satisfies a "double self-similarity"
condition: not only must each cell encode the same curvature (H1), but the
LAG EFFECT per cell must also be self-similar.*

The lag per cell is:

$$a_{\text{lag,cell}} \sim \tau_{\text{graph}} \cdot \frac{l_0}{c} \cdot v_r \cdot \frac{GM}{r^3}
\tag{15}$$

The number of cells that contribute coherently to the lag is:

$$N_{\text{coh}} \sim \frac{\ell_{\text{coh}}}{l_0} = \frac{v_r \cdot \tau_{\text{graph}}}{c} \tag{16}$$

This is a constant (independent of $r$). So the total lag is just
$N_{\text{coh}} \times a_{\text{lag,cell}}$, and the extra factor doesn't help.

### 4.4 Possible origin: graph entropy condition

**Hypothesis (H3).** *The graph lattice scale is set by an entropy condition:
the number of distinguishable graph configurations per unit volume equals a
universal constant.*

The number of graph configurations for $N$ nodes in a volume $V$ with metric
constraint $g_{ij}$ scales as:

$$\mathcal{N} \sim \left(\frac{V}{l_0^3}\right)! \cdot \exp(-S_{\text{EH}}[g])
\tag{17}$$

where $S_{\text{EH}}$ is the Einstein-Hilbert action. For a Schwarzschild field:

$$S_{\text{EH}} \sim \int R \sqrt{g}\, d^3x \sim \int \frac{GM}{r^3} \cdot r^2\, dr
\sim GM \ln(r) \tag{18}$$

The entropy per unit volume condition $\partial_r(\ln\mathcal{N}/V) = 0$ gives
a transcendental equation for $l_0(r)$ that does not have a clean power-law
solution. This approach requires further development.

---

## 5. Honest assessment

### What has been achieved

1. The **Hessian self-similarity** condition (H1) provides a principled
   derivation of $\alpha = 3/4$, which reduces the Pioneer range variation
   from $42\times$ (Scenario A) to $6.6\times$.

2. The exponent $\alpha = 3/4$ is **unique** under H1 — no other value
   satisfies constant dimensionless curvature per cell.

3. The gap from $\alpha = 3/4$ to $\alpha = 3/2$ is exactly a factor of 2
   in the exponent, suggesting a "squared" physical condition exists.

### What has NOT been achieved

1. No first-principles argument produces $\alpha = 3/2$ exactly.

2. The "double self-similarity" and entropy approaches do not close the gap.

3. $\alpha = 3/2$ remains **phenomenologically fixed** by Pioneer data.

### Recommended framing for the paper

> *"Under the assumption that the QNG graph resolves curvature self-similarly
> (constant dimensionless Hessian per cell), the lattice exponent is
> $\alpha = 3/4$, reducing the Pioneer anomaly distance variation from
> $42\times$ to $6.6\times$. The observational requirement of a constant
> anomaly further constrains $\alpha = 3/2$, which may arise from a
> higher-order self-similarity condition involving the lag coherence
> structure. Closing this gap is an open theoretical challenge."*

---

## 6. Path forward

1. **Investigate whether the Σ field equation self-consistently determines
   $l_0(r)$.** If $\partial_i(g^{ij}\partial_j\Sigma) = 4\pi\rho$ is solved
   on a graph with $l_0(r)$, does the solution converge only for $\alpha = 3/2$?

2. **Renormalization group analysis.** In lattice field theory, the lattice
   spacing runs with energy scale. If QNG has an analogous RG flow, $l_0(r)$
   would be determined by the beta function of the graph coupling. The exponent
   $\alpha$ would then be a critical exponent.

3. **Numerical experiment.** Vary $\alpha$ in QNG graph simulations (not solar
   system, but abstract 3D) and measure which value produces the most
   stable/self-consistent metric recovery. If $\alpha = 3/2$ is preferred
   numerically, that would be strong evidence for an underlying principle.
