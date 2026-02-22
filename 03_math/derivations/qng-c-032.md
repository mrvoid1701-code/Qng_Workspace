# QNG-C-032 Derivation

- Claim statement: Node stability is `Sigma_i in [0,1]` with multiplicative components.
- Source page(s): `page-028,page-072`
- Claim status/confidence: `formalized / high`
- Math maturity: `v2 (core-closure)`
- Closure note: `01_notes/core-closure-v1.md`

## Definitions

- Stability:
  - `Sigma_i in [0,1]`
- Decomposition:
  - `Sigma_i = Sigma_chi,i * Sigma_struct,i * Sigma_temp,i * Sigma_phi,i`
- Existence condition:
  - node survives if `Sigma_i >= Sigma_min`

## Component Closure

To keep dimensions explicit:

```text
Sigma_chi,i    = exp(-|chi_i - chi_ref| / chi_ref)
Sigma_struct,i = exp(-|k_i - k_eq| / k_eq)
Sigma_temp,i   = exp(-|Delta_t_local - tau_i| / tau_i)
Sigma_phi,i    = (1 + cos(Delta_phi_i)) / 2
tau_i          = alpha_tau * chi_i
```

All component terms are dimensionless and bounded in `(0,1]`, therefore:

```text
0 <= Sigma_i <= 1
```

## Derivation Steps

1. Start from multiplicative stability assumption.
2. Define bounded component maps for `chi`, structure (`k_i`/`V_i`), temporal coherence (`tau_i`), and phase.
3. Show each factor is dimensionless and in `[0,1]`.
4. Conclude boundedness for product.
5. Connect to survival gate `Sigma_i >= Sigma_min` and update rule `U`.

## Result

- `Sigma_i` is mathematically bounded.
- `Sigma_i` links directly to:
  - node persistence,
  - birth/death gating in `C-029`,
  - volume dynamics through `k_i`.

## Checks

- Dimensional consistency:
  - only ratio/exponential arguments are dimensionless.
- Bound consistency:
  - product of bounded factors remains bounded.
- Coupling consistency:
  - `tau_i = alpha_tau * chi_i` ties `chi` to observables through delay tests.

## Next Action

- Validate `Sigma`-gated behavior using:
  - `T-V-02` stationary spectrum gate
  - `T-V-03` attractor/identity gate

