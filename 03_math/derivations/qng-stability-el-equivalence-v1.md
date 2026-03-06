# QNG Stability - Formal EL Equivalence (v1, corrected)

- Date: 2026-03-06
- Status: formal theorem-lane note (no formula changes)
- Scope: prove that the implemented one-step update is an explicit projected Euler-EL step (first-order variational discretization)
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

## 2) Lagged Local Potential

Define the lagged per-node potential:

```text
V_i^t(Sigma_i, chi_i, phi_i) =
  (k_cl/2) * (Sigma_i - Sigma_hat_i^t)^2
  + (k_sm/2) * (Sigma_i - Sigma_neigh_i^t)^2
  + (k_chi/2) * chi_i^2
  + k_mix * chi_i * (Sigma_i - Sigma_neigh_i^t)
  + k_phi * (1 - cos(phi_i - phi_neigh_i^t))
```

with all lagged quantities (`Sigma_hat_i^t`, neighbor means) frozen from `X^t`.

The corresponding gradient flow is:

```text
dot X = - grad V^t(X),   where V^t = Sum_i V_i^t.
```

Nodewise gradients evaluated at `X^t`:

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

## 3) Explicit Euler-EL Step (What Code Implements)

The implemented deterministic core is:

```text
Sigma_i^+ = Sigma_i^t - alpha_Sigma * grad_Sigma_i^t
chi_i^+   = chi_i^t   - alpha_chi   * grad_chi_i^t
phi_i^+   = phi_i^t   - alpha_phi   * grad_phi_i^t
```

then additive noise is applied in `chi,phi` channels:

```text
chi_i^+ <- chi_i^+ + eta_chi,i^t
phi_i^+ <- phi_i^+ + eta_phi,i^t
```

then projection/retraction:

```text
Sigma_i^{t+1} = clip01(Sigma_i^+)
chi_i^{t+1}   = chi_i^+
phi_i^{t+1}   = wrap(phi_i^+)
```

So code is exactly a projected explicit Euler step for the lagged EL gradient flow.

## 4) Equivalent Variational Surrogate (Linearized Proximal Form)

Define the first-order surrogate around `X^t`:

```text
J_t^lin(X; X^t) =
  Sum_i [
    (Sigma_i - Sigma_i^t)^2 / (2*alpha_Sigma)
    + (chi_i   - chi_i^t)^2 / (2*alpha_chi)
    + dS1(phi_i, phi_i^t)^2 / (2*alpha_phi)
    + <grad V_i^t(X^t), X_i - X_i^t>
  ]
```

Its minimizer is explicit and equals:

```text
X^{t+1,unproj} = X^t - A grad V^t(X^t)
```

with `A = diag(alpha_Sigma, alpha_chi, alpha_phi)` (per channel), then projected to `[0,1] x R x S1`.

Hence:

```text
one_step deterministic core == argmin_X J_t^lin(X; X^t) followed by clip/wrap
```

This is the correct exact statement.

## 5) Important Correction About Fully Proximal `J_t`

If one instead minimizes:

```text
J_t(X) = prox_term + V^t(X)
```

with bilinear `k_mix * chi_i * Sigma_i` coupling, stationarity is generally an implicit coupled system. That map is not identical to the explicit code step unless further linearization/splitting assumptions are added.

Therefore this note does **not** claim exact equality with the fully implicit proximal map.

## 6) Relation to the Full Non-Lagged Action

If one differentiates a fully coupled same-time action where
`Sigma_hat_i` and neighbor means are treated as functions of all node variables,
additional chain terms appear.

Hence:

```text
U_full_EL = U_lagged_EL + Delta_full
```

This note proves exact equivalence for the explicit lagged linearized EL step (implemented lane), and keeps `Delta_full` as separate theorem-lane content.

## 7) Audit Implication

This removes "numeric-only" ambiguity without over-claiming:

1. the checker is a numerical verification layer,
2. this note is the formal statement of what object is being verified,
3. no thresholds/formulas are altered by this formalization.
