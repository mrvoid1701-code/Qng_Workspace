# QNG Stability Variational Update V1

- Date: 2026-03-03
- Status: locked (v1 strict)
- Depends on: `03_math/derivations/qng-stability-action-v1.md`

## Euler-Lagrange to Discrete Update

For local action density `L_i`:

```text
grad_Sigma_i = dL_i / dSigma_i
grad_chi_i   = dL_i / dchi_i
grad_phi_i   = dL_i / dphi_i
```

Overdamped variational update (explicit Euler):

```text
Sigma_i(t+1) = clip(Sigma_i(t) - alpha_Sigma * grad_Sigma_i(t), 0, 1)
chi_i(t+1)   = chi_i(t)   - alpha_chi   * grad_chi_i(t) + eta_chi,i(t)
phi_i(t+1)   = wrap(phi_i(t) - alpha_phi * grad_phi_i(t) + eta_phi,i(t))
```

where `eta_*` are preregistered local perturbations.

## Closed Gradients (v1 strict)

Using the action in `qng-stability-action-v1.md`:

```text
grad_Sigma_i =
  k_cl * (Sigma_i - Sigma_hat_i)
  + k_sm * (Sigma_i - <Sigma>_Adj(i))
  + k_mix * chi_i

grad_chi_i =
  k_chi * chi_i
  + k_mix * (Sigma_i - <Sigma>_Adj(i))

grad_phi_i =
  k_phi * sin(phi_i - <phi>_Adj(i))
```

## Variational Residual

Per-step residuals are monitored as:

```text
r_Sigma_i = Sigma_i(t+1) - clip(Sigma_i(t) - alpha_Sigma * grad_Sigma_i(t), 0, 1)
r_chi_i   = chi_i(t+1)   - (chi_i(t) - alpha_chi * grad_chi_i(t) + eta_chi,i(t))
r_phi_i   = angle_diff(phi_i(t+1), phi_i(t) - alpha_phi * grad_phi_i(t) + eta_phi,i(t))
```

with gate statistic:

```text
max_residual = max_i,t (|r_Sigma_i|, |r_chi_i|, |r_phi_i|)
```

This provides a direct "update is variational" diagnostic for stress runs.

Alpha-drift diagnostic is evaluated on active nodes only (`|chi_i| >= chi_active_min`)
to avoid singular behavior in the near-zero normalization regime.

## Minimal Stability Statements (v1)

Under bounded step sizes and local finite graph neighborhoods:

1. Boundedness of `Sigma` is guaranteed by projection (`clip`).
2. Metric positivity proxy is guaranteed when `g_ii = 1 + beta_g * Sigma_i` with `beta_g > 0`.
3. One-step locality follows from neighbor-only gradients (`Adj(i)` dependence only).

Formal existence/uniqueness proofs for full coupled nonlinear dynamics are deferred to future theorem lane.
