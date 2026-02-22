# QNG-C-029 Derivation

- Claim statement: Universe dynamics follow discrete updates `N_i(t+1) = U(...)`.
- Source page(s): `page-027,page-072`
- Claim status/confidence: `formalized / high`
- Math maturity: `v2 (core-closure)`
- Closure note: `01_notes/core-closure-v1.md`

## Definitions

- Node state:
  - `N_i(t) = (V_i(t), chi_i(t), phi_i(t))`
- Graph:
  - `G(t) = (N(t), E(t))`
- Stability:
  - `Sigma_i(t) in [0, 1]`
- Existence gate:
  - active if `Sigma_i(t) >= Sigma_min`

## Frozen Update Form

```text
N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))
```

Expanded closure:

```text
chi_i(t+1) = chi_i(t) + F_chi,i(local state, eta_i)
phi_i(t+1) = phi_i(t) + F_phi,i(local state, eta_i)
k_i(t+1)   = max(1, k_i(t) + Delta_k_i^+ - Delta_k_i^-)
V_i(t+1)   = k_i(t+1) * V_0
```

with

```text
Delta_k_i^+ = floor(beta_plus * max(0, Sigma_i - Sigma_grow))
Delta_k_i^- = floor(beta_minus * max(0, Sigma_shrink - Sigma_i))
```

and topology gates:

```text
if Sigma_i < Sigma_min: remove node i
if Sigma_i >= Sigma_birth and coherence gate passes: spawn child node
```

## Derivation Steps

1. Start from the primitive discrete claim `N_i(t+1)=U(...)`.
2. Resolve state variables explicitly as `(V_i, chi_i, phi_i)` to eliminate ambiguity in `U`.
3. Freeze `V` dynamics via quantized rule `V_i = k_i V_0` with integer `k_i`.
4. Add existence/birth gates tied to `Sigma_i` to complete graph update.
5. Keep stochasticity through `eta_i(t)` only in local terms (`F_chi`, `F_phi`, local gate jitter).

## Result

- The update is now closed at rule level:
  - state update,
  - node birth/death,
  - volume quantization,
  - local-only dependence.
- This makes `C-029` executable in simulation and testable with explicit gates.

## Checks

- Dimensional:
  - `V_0` carries `L^3`; all `k_i` terms are dimensionless.
- Locality:
  - all updates depend on `Adj(i)` only.
- Limit:
  - with birth disabled and `Delta_k_i^+ = Delta_k_i^- = 0`, update reduces to fixed-size discrete dynamics.

## Next Action

- Validate closure behavior with:
  - `T-V-01` conservation/growth gate
  - `T-V-03` attractor/identity gate
  - `T-V-04` GR-limit kill switch

