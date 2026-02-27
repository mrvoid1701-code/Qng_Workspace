# The α Story: A Coherent Narrative — v1

**Status:** Final narrative synthesis
**Date:** 2026-02-27
**Based on:** `qng-alpha-derivation-v1.md`
**Purpose:** Paper-ready framing of the α situation; honest about what is and is not derived

---

## The one-sentence version

> *Under the Hessian self-similarity assumption (H1), QNG predicts $\alpha = 3/4$;
> the observationally required value $\alpha = 3/2$ is exactly twice the derived
> value, leaving a factor-of-two gap that is an open theoretical challenge.*

---

## 1. What α controls

The straton lattice scale $l_0$ varies with position through the gradient of the
stability field:

$$l_0(r) = l_{0,\text{ref}} \left(\frac{|\nabla\Sigma_{\text{ref}}|}{|\nabla\Sigma(r)|}\right)^\alpha$$

In the solar system ($\Sigma = -GM/r$, so $|\nabla\Sigma| = GM/r^2$):

$$l_0(r) \propto r^{2\alpha}$$

The lag acceleration scales as $a_{\text{lag}} \propto r^{2\alpha - 3}$.
For the anomaly to be **distance-independent** (as Pioneer requires), we need:

$$2\alpha - 3 = 0 \quad\Longrightarrow\quad \alpha = \frac{3}{2}$$

This is the observational constraint. The question is whether QNG can derive it.

---

## 2. What QNG predicts (under H1)

**Assumption H1 (Hessian self-similarity):** The dimensionless product
$\xi = |H|\,l_0^2$ is constant across scales.

The Hessian magnitude $|H| \propto r^{-3}$ (Frobenius norm of the Kepler Hessian).
Requiring $\xi = \text{const}$:

$$|H|\,l_0^2 = \text{const} \quad\Longrightarrow\quad l_0 \propto |H|^{-1/2} \propto r^{3/2}$$

Since $l_0 \propto |\nabla\Sigma|^{-\alpha} = r^{2\alpha}$:

$$\boxed{\alpha_{\text{H1}} = \frac{3}{4}}$$

This reduces the Pioneer variation from $42\times$ (constant $l_0$) to $6.6\times$
(across 20–70 AU). It is a genuine improvement, but it falls short of the required
constant.

---

## 3. The gap: why $\alpha = 3/2$ is not derived

The self-similarity argument gives $\alpha = 3/4$. Three natural physical arguments
(radial resolution, orbital period scaling, coherence length condition) all give
$\alpha \in \{1/2, 3/4\}$. None produce $3/2$.

The gap is exact:

$$\alpha_{\text{Pioneer}} = 2 \times \alpha_{\text{H1}} \tag{factor-of-two gap}$$

Attempted resolutions tried and ruled out:
- Double self-similarity (cascade): still gives $3/4$
- Coherence length condition ($l_0 \propto$ mean free path): gives $3/4$
- Entropy condition on graph complexity: transcendental, no clean solution

The factor-of-two gap is a **genuine open problem**, not a tuning parameter.

---

## 4. What this means

**For the straton framework:** The constant-anomaly result ($\alpha = 3/2$) cannot
currently be derived from first principles. It is an observational input, not a
prediction. This is an honest limitation.

**For the theory:** The derived value $\alpha = 3/4$ is not arbitrary — it follows
uniquely from H1 and is falsifiable. If future data show $a_{\text{lag}} \propto r^{-3/2}$
(not constant), that would confirm $\alpha = 3/4$ and rule out the Pioneer interpretation.

**For the paper:** Two claims can be made cleanly:

1. *Derived (under H1):* $\alpha = 3/4$ follows from Hessian self-similarity.
   This alone reduces the Pioneer variation from 42× to 6.6×.

2. *Observational constraint:* $\alpha = 3/2$ is required for a constant anomaly.
   The gap to the derived value is acknowledged as a theoretical challenge.

---

## 5. Three paths to closing the gap

**Path A — $\Sigma$ self-consistency:**
Require that $l_0(r)$ and $\Sigma(r)$ satisfy a self-consistent field equation:

$$\Box\Sigma = \rho + f(l_0, \Sigma) \quad\text{with}\quad l_0 = l_0(\Sigma)$$

If $f$ couples back through the gradient in a specific way, this might force
$\alpha = 3/2$. Preliminary analysis has not found this, but the space of
coupling functions has not been exhausted.

**Path B — Renormalization group:**
Treat $l_0$ as a running coupling in the graph's effective action.
The fixed point of the RG flow might select $\alpha = 3/2$ in the IR limit.
This is speculative but physically motivated by the analogy with lattice QCD
(where the lattice spacing flows under the RG).

**Path C — Numerical experiment:**
Implement the QNG graph in 3D and measure how $l_0^{\text{eff}}$ (the effective
lattice scale seen by a propagating signal) depends on $r$. If the theory is
self-consistent, the numerically measured $\alpha^{\text{eff}}$ will select the
correct value without assuming H1.

---

## 6. Recommended paper language

> "Under the Hessian self-similarity hypothesis (H1), the straton lattice scale
> satisfies $\xi = |H|\,l_0^2 = \mathrm{const}$, which uniquely gives $\alpha = 3/4$
> and a lag acceleration $a_{\mathrm{lag}} \propto r^{-3/2}$. This reduces the
> variation across 20–70 AU from $42\times$ to $6.6\times$. A distance-independent
> anomaly requires $\alpha = 3/2$, exactly twice the self-similar value. This gap
> is an open theoretical challenge. We report $\alpha = 3/4$ as a derived consequence
> of H1 and $\alpha = 3/2$ as an observational requirement; the reconciliation is
> left to future work."

---

## 7. The complete α landscape

| $\alpha$ | Origin | $a_{\text{lag}}$ scaling | Variation 20–70 AU | Status |
|---|---|---|---|---|
| 0 | Constant $l_0$ | $r^{-3}$ | $42\times$ | Excluded (Scenario A) |
| 1/2 | Radial resolution | $r^{-2}$ | $11\times$ | Tentative |
| **3/4** | **Hessian self-similarity (H1)** | $r^{-3/2}$ | $6.6\times$ | **Derived** |
| 3/2 | Pioneer requirement | $r^0$ | $1\times$ | Required, not derived |

The derived value $\alpha = 3/4$ is marked in bold. All other values in this
table are either excluded by data (0) or are observational constraints (3/2).
The intermediate value 1/2 is a suggestive but not fully derived result.
