# QNG Stability - Formal EL Equivalence (v1)

- Date: 2026-03-06
- Status: formal theorem-lane note (no formula changes)
- Scope: prove that the implemented one-step update is a discrete EL/proximal step for a lagged local action
- Related implementation: `scripts/tools/run_stability_stress_v1.py::one_step`

## 1) Setup

Let the state at step `t` be:

```text
X^t = (Sigma^t, chi^t, phi^t)
```

with domains:

```text
Sigma_i in [0,1], chi_i in R, phi_i in (-pi, pi].
```

For each node `i`, define frozen local coefficients from `X^t`:

```text
Sigma_hat_i^t
Sigma_neigh_i^t = <Sigma^t>_Adj(i)
phi_neigh_i^t   = <phi^t>_Adj(i)  (circular mean)
```

where `Sigma_hat_i^t` is the same multiplicative closure term used in the runner.

## 2) Lagged Local Action

Define the lagged per-node potential:

```text
V_i^t(Sigma_i, chi_i, phi_i) =
  (k_cl/2) * (Sigma_i - Sigma_hat_i^t)^2
  + (k_sm/2) * (Sigma_i - Sigma_neigh_i^t)^2
  + (k_chi/2) * chi_i^2
  + k_mix * chi_i * (Sigma_i - Sigma_neigh_i^t)
  + k_phi * (1 - cos(phi_i - phi_neigh_i^t))
```

and the incremental functional:

```text
J_t(X) =
  Sum_i [
    (Sigma_i - Sigma_i^t)^2 / (2*alpha_Sigma)
    + (chi_i   - chi_i^t)^2   / (2*alpha_chi)
    + dS1(phi_i, phi_i^t)^2   / (2*alpha_phi)
    + V_i^t(Sigma_i, chi_i, phi_i)
  ]
```

`dS1` is geodesic distance on the circle.

This is the standard minimizing-movement / proximal-EL form for one explicit step with lagged coefficients.

## 3) Nodewise Stationarity

For each node `i`, stationarity of `J_t` gives:

```text
0 = (Sigma_i - Sigma_i^t)/alpha_Sigma + dV_i^t/dSigma_i
0 = (chi_i   - chi_i^t)  /alpha_chi   + dV_i^t/dchi_i
0 = grad_phi geodesic term + dV_i^t/dphi_i
```

with gradients:

```text
dV_i^t/dSigma_i =
  k_cl * (Sigma_i - Sigma_hat_i^t)
  + k_sm * (Sigma_i - Sigma_neigh_i^t)
  + k_mix * chi_i

dV_i^t/dchi_i =
  k_chi * chi_i
  + k_mix * (Sigma_i - Sigma_neigh_i^t)

dV_i^t/dphi_i =
  k_phi * sin(phi_i - phi_neigh_i^t)
```

Therefore the unconstrained explicit step is:

```text
Sigma_i^+ = Sigma_i^t - alpha_Sigma * grad_Sigma_i^t
chi_i^+   = chi_i^t   - alpha_chi   * grad_chi_i^t + eta_chi,i^t
phi_i^+   = phi_i^t   - alpha_phi   * grad_phi_i^t + eta_phi,i^t
```

and the implemented constrained step is:

```text
Sigma_i^{t+1} = clip01(Sigma_i^+)
chi_i^{t+1}   = chi_i^+
phi_i^{t+1}   = wrap(phi_i^+)
```

which is exactly projected proximal-EL on `[0,1] x R x S1`.

## 4) Proposition (Exact Equivalence for the Implemented Lane)

For fixed adjacency, fixed constants, and fixed RNG draws `(eta_chi, eta_phi)` at step `t`:

```text
one_step(X^t) == ProjectedProximalELStep(J_t; X^t)
```

where `J_t` is the lagged local action above.

So the implemented update is formally variational in the discrete/proximal sense for the frozen lagged action.

## 5) Relation to the Full Non-Lagged Action

If one differentiates a fully coupled same-time action where
`Sigma_hat_i` and neighbor means are treated as functions of all node variables,
additional chain terms appear.

Hence:

```text
U_full_EL = U_lagged_EL + Delta_full
```

This note proves exact equivalence for `U_lagged_EL` (the implemented lane), and keeps `Delta_full` as a separate theorem-lane object.

## 6) Audit Implication

This removes "numeric-only" ambiguity:

1. the checker is a numerical verification layer,
2. this note is the formal statement of what object is being verified,
3. no thresholds/formulas are altered by this formalization.
