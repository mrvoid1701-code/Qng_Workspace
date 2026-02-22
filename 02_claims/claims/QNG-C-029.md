# QNG-C-029

- Status: formalized
- Confidence: high
- Source page(s): page-027,page-072
- Related derivation: 03_math/derivations/qng-c-029.md
- Closure reference: 01_notes/core-closure-v1.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Universe dynamics proceed through discrete local updates:

```text
N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))
```

with node state `N_i = (V_i, chi_i, phi_i)` and explicit birth/death gates driven by `Sigma_i`.

## Assumptions

- A1. Node-level discrete updates are fundamental.
- A2. Updates are local in graph adjacency.
- A3. State variables are exactly `(V_i, chi_i, phi_i)` in closure v1.
- A4. Existence is gated by `Sigma_i >= Sigma_min`.
- A5. Stochastic term `eta_i` captures unresolved micro-noise only.

## Mathematical Form

- State update:
  - `chi_i(t+1) = chi_i(t) + F_chi,i(...)`
  - `phi_i(t+1) = phi_i(t) + F_phi,i(...)`
  - `V_i(t+1) = k_i(t+1) * V_0`
- Birth/death topology:
  - remove node if `Sigma_i < Sigma_min`
  - spawn node if `Sigma_i >= Sigma_birth` and coherence gate passes

## Potential Falsifier

- Required non-local updates to match data.
- Inability to produce stable coarse-grained dynamics under local `U`.
- Contradictory behavior in closure gates (`T-V-01/T-V-03/T-V-04`).

## Evidence / Notes

- Formal closure is now explicit and executable.
- Supports direct simulation checks for conservation/growth, attractor robustness, and GR-limit sanity.

## Next Action

- Execute and track:
  - `T-V-01` conservation/growth gate
  - `T-V-03` attractor/identity gate
  - `T-V-04` GR-limit kill switch
