# QNG Stability Action V1

- Date: 2026-03-03
- Status: locked (v1 strict)
- Variables: `Sigma_i`, `chi_i`, `phi_i`

## Conventions

1. Indexing:
   - `i` = node index
   - `j in Adj(i)` = local neighbors
2. Time:
   - discrete steps `t = 0,1,...,T`
3. Units/signs:
   - `Sigma` dimensionless, bounded in `[0,1]`
   - `chi` dimensionless in this normalized closure
   - `phi` in radians (wrapped to `(-pi, pi]`)
   - all coupling constants positive unless explicitly stated

## Closure Components

`Sigma_hat_i` is the multiplicative closure target:

```text
Sigma_hat_i = clip(Sigma_chi,i * Sigma_struct,i * Sigma_temp,i * Sigma_phi,i, 0, 1)
```

with:

```text
Sigma_chi,i    = exp(-|chi_i - chi_ref| / chi_ref)
Sigma_struct,i = exp(-|k_i - k_eq| / k_eq)
Sigma_temp,i   = exp(-|Delta_t_local,i - tau_i| / tau_i)
Sigma_phi,i    = (1 + cos(phi_i - <phi>_Adj(i))) / 2
tau_i          = alpha_tau * |chi_i|
```

## Discrete Action

For a trajectory `(Sigma_t, chi_t, phi_t)`:

```text
S = Sum_t Sum_i [L_i,t]
```

with:

```text
L_i,t =
  (k_cl/2) * (Sigma_i,t - Sigma_hat_i,t)^2
  + (k_sm/2) * (Sigma_i,t - <Sigma>_Adj(i),t)^2
  + (k_chi/2) * chi_i,t^2
  + k_mix * chi_i,t * (Sigma_i,t - <Sigma>_Adj(i),t)
  + k_phi * (1 - cos(phi_i,t - <phi>_Adj(i),t))
```

Notes:

1. `k_cl, k_sm, k_chi, k_phi > 0` enforce convex local penalties.
2. `k_mix` is the only signed coupling term between `chi` and `Sigma`.
3. This is a local graph action; no non-local kernel terms are introduced in v1 strict.

## Why This Form

1. It encodes bounded `Sigma` attraction to closure target `Sigma_hat`.
2. It controls roughness through neighbor penalties.
3. It keeps phase coupling periodic and bounded.
4. It yields explicit local gradients for deterministic update/gating.
