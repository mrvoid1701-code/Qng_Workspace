# QNG Post-Newtonian Structure (v1)

Date: 2026-02-25  
Scope: Linearized (post-Newtonian) form of the QNG field and acceleration equations.  
Assumption: weak-field metric perturbation |h| ≪ 1 with g_{ij} = δ_{ij} + h_{ij}.

## 1. Linearized field equation
Starting point (QNG scalar sector):
\[
\partial_i\!\left(g^{ij}\,\partial_j \Sigma\right) = 4\pi \rho.
\]
Write the inverse metric to first order:
\[
g^{ij} = \delta^{ij} - h^{ij} + O(h^2).
\]
Plug in and expand:
\[
\partial_i\!\left[(\delta^{ij} - h^{ij})\,\partial_j \Sigma\right]
= \partial_i\partial^i \Sigma\;-\;\partial_i\!\left(h^{ij}\partial_j \Sigma\right) + O(h^2).
\]
To first order, the flat Poisson operator is corrected by a metric–field coupling term:
\[
\boxed{\;\partial^2 \Sigma - \partial_i(h^{ij}\partial_j\Sigma) = 4\pi\rho + O(h^2)\;}
\]
which is the QNG analogue of the PN correction to the Poisson equation.

## 2. Linearized acceleration
QNG acceleration is \(a^i = -g^{ij}\partial_j \Sigma\).
Expanding:
\[
a^i = -(\delta^{ij}-h^{ij})\partial_j \Sigma + O(h^2)
= -\partial^i\Sigma \;+\; h^{ij}\partial_j \Sigma + O(h^2).
\]
Therefore the first-order correction to Newtonian acceleration is
\[
\boxed{\;\delta a^i = +\,h^{ij}\partial_j \Sigma\;}
\]
(the sign follows from the -g^{ij} in the definition; if one defines \(h^{ij}=-h_{ij}\) the equivalent form is \(\delta a^i = -h_{ij}\partial^j\Sigma\)). This matches the coupling term that also appears in the corrected Poisson operator.

## 3. Comparison with GR linearized (post-Newtonian) form
In weak-field GR, with metric \(g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}\) and slow-motion, the leading correction to acceleration is
\[
a^i_{\text{GR}} \simeq -\Gamma^i_{00} \approx -\tfrac{1}{2}\partial_i h_{00}.
\]
Interpretation:
- GR: PN correction ties acceleration to gradients of the time-time perturbation \(h_{00}\).
- QNG: PN correction ties acceleration to spatial metric perturbation \(h_{ij}\) contracted with \(\partial_j\Sigma\).

Structural similarity:
- Both produce a linear-in-\(h\) correction to Newtonian acceleration.
- Both arise from linearizing the covariant derivative acting on the potential (Newtonian potential in GR; \(\Sigma\) in QNG).
- In gauges where \(h_{00}\) in GR plays the role of the potential, identifying \(h_{00}\sim 2\Sigma\) shows the same dependence on \(\partial_i h\) vs \(\partial_i \Sigma\); QNG encodes it through \(h^{ij}\partial_j\Sigma\) rather than \(\partial_i h_{00}\).

Key takeaway: QNG’s linearized correction reproduces the expected PN “metric times gradient” structure, differing only in which metric component carries the perturbation (spatial \(h_{ij}\) vs temporal \(h_{00}\)), so the phenomenology of small deviations from Newtonian gravity aligns with the GR PN template.
