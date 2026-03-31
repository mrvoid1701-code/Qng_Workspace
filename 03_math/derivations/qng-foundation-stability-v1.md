# QNG Foundation Stability V1

- Date: 2026-03-06
- Status: locked foundation note (v1)
- Scope: discrete stability core for `Sigma, chi, phi`

## 1) Discrete Model (Fixed)

Graph and time:

- graph `G = (V, E)`, node index `i in V`, neighbors `Adj(i)`
- discrete time `t = 0,1,...,T`

State variables:

- `Sigma_i^t in [0,1]`
- `chi_i^t in R`
- `phi_i^t in (-pi, pi]`

Frozen constants (v1 lane):

- `alpha_Sigma, alpha_chi, alpha_phi, alpha_tau`
- `chi_ref, k_cl, k_sm, k_chi, k_mix, k_phi`
- `tau_floor, dt_local_beta`

Fixed-vs-free:

- fixed: equation form, signs, variable domains, projection/wrap operators
- free (per prereg run): seed ranges, block specs, stress grid over
  `edge_prob, chi_scale, noise, phi_shock`

## 2) Discrete Action

Per-node closure target:

```text
Sigma_hat_i = clip(Sigma_chi,i * Sigma_struct,i * Sigma_temp,i * Sigma_phi,i, 0, 1)
```

with:

```text
Sigma_chi,i    = exp(-|chi_i - chi_ref| / chi_ref)
Sigma_struct,i = exp(-|k_i - k_eq| / k_eq)
Sigma_temp,i   = exp(-|Delta_t_local,i - tau_i| / tau_i)
Sigma_phi,i    = (1 + cos(phi_i - <phi>_Adj(i))) / 2
tau_i          = max(tau_floor, alpha_tau * |chi_i|)
```

Action:

```text
S = Sum_t Sum_i L_i,t
```

```text
L_i,t =
  (k_cl/2) * (Sigma_i,t - Sigma_hat_i,t)^2
  + (k_sm/2) * (Sigma_i,t - <Sigma>_Adj(i),t)^2
  + (k_chi/2) * chi_i,t^2
  + k_mix * chi_i,t * (Sigma_i,t - <Sigma>_Adj(i),t)
  + k_phi * (1 - cos(phi_i,t - <phi>_Adj(i),t))
```

Sign convention:

- `k_cl, k_sm, k_chi, k_phi > 0`
- `k_mix` signed coupling term

## 3) Discrete EL (Proxy Form Used by Current Update)

Proxy local gradients:

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

Overdamped discrete update:

```text
Sigma_i(t+1) = clip(Sigma_i(t) - alpha_Sigma * grad_Sigma_i(t), 0, 1)
chi_i(t+1)   = chi_i(t) - alpha_chi * grad_chi_i(t) + eta_chi,i(t)
phi_i(t+1)   = wrap(phi_i(t) - alpha_phi * grad_phi_i(t) + eta_phi,i(t))
```

## 4) U_current vs U_EL Mapping

Define:

- `U_current`: implemented update used in `run_stability_stress_v1.py`
- `U_EL_proxy`: EL-proxy update above (same formula family)
- `U_EL_unprojected`: same as proxy before `clip/wrap` projection

Residual used in checker:

```text
R = U_current - U_EL_unprojected
```

Component form:

```text
R_Sigma = Sigma_next - (Sigma - alpha_Sigma * grad_Sigma)
R_chi   = chi_next   - (chi   - alpha_chi   * grad_chi + eta_chi)
R_phi   = angle_diff(phi_next, phi - alpha_phi * grad_phi + eta_phi)
```

Interpretation:

- `R_Sigma` captures bounded projection (`clip`) when raw step exits `[0,1]`
- `R_chi` should be machine-zero under explicit implementation
- `R_phi` is measured modulo `2pi` and should be machine-zero

## 5) Ansatz Note (Full EL vs Proxy EL)

The v1 proxy gradients treat closure coupling in reduced form.
In full EL for the action, additional chain-rule terms can appear from
`Sigma_hat` dependence (notably in `chi` and `phi` channels).

So:

```text
U_EL_full = U_EL_proxy + Delta_ansatz
```

Current checker quantifies `U_current` consistency with `U_EL_unprojected`
for the frozen proxy lane. It does **not** claim `Delta_ansatz = 0`.
`Delta_ansatz` remains an explicit open-theory term for future v2 theorem lane.
