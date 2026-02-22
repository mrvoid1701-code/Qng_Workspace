# Core Closure v1 (Node + Volume + Chi)

Date: 2026-02-21  
Scope: freeze a minimal, testable closure for `N_i`, `V_i`, `chi_i`, `Sigma_i`, and update operator `U`.

## 1) Ontology

- Node state:
  - `N_i(t) = (V_i(t), chi_i(t), phi_i(t))`
- Graph geometry:
  - `G(t) = (N(t), E(t))`
- Stability:
  - `Sigma_i(t) in [0, 1]`
- Existence gate:
  - node exists if `Sigma_i >= Sigma_min`

## 2) Volume Definition (What Is V0)

- `V_0` is the reference node volume quantum for coarse-grained physical volume.
- Units:
  - `V_0` has dimension `L^3`.
  - `V_i = k_i * V_0`, with integer `k_i >= 1` for active nodes.
- Interpretation:
  - `V_i` is not an embedding coordinate cell.
  - `V_i` is an effective relational volume weight used in coarse-grained observables.

## 3) Frozen Volume Rule for v1

Chosen for v1: **V-B (expansive rule)**, because it is directly testable against `C-103/C-104`.

- Birth gate:
  - if `Sigma_i >= Sigma_birth` and local coherence gate passes, create one child node `k_new = 1`.
- Death gate:
  - if `Sigma_i < Sigma_min`, node is removed.
- Local volume update:
  - `k_i(t+1) = max(1, k_i(t) + Delta_k_i^+ - Delta_k_i^-)`
  - `Delta_k_i^+ = floor(beta_plus * max(0, Sigma_i - Sigma_grow))`
  - `Delta_k_i^- = floor(beta_minus * max(0, Sigma_shrink - Sigma_i))`
- Total relational volume:
  - `V_tot(t) = sum_{i in N(t)} V_i(t)`
  - not globally conserved in v1 (`dV_tot/dt >= 0` expected in expansion regime).

## 4) Chi Interpretation (v1 choice)

Chosen for v1: **Option A (identifiable memory coupling)**.

- `tau_i = alpha_tau * chi_i`
- `chi_i` is used as memory coupling, not as a separately conserved fluid.
- Identifiability target:
  - infer `tau` from trajectory/timing tests, then map to `chi` through fixed `alpha_tau`.

## 5) Stability and Update Operator

- Multiplicative stability closure:
  - `Sigma_i = clip(Sigma_chi,i * Sigma_struct,i * Sigma_temp,i * Sigma_phi,i, 0, 1)`
- Node update:
  - `N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))`
- Existence and topology update:
  - remove nodes with `Sigma_i < Sigma_min`
  - add nodes only via frozen birth gate
  - update edges by local adjacency rule

## 6) Conserved vs Non-Conserved in v1

- Conserved:
  - positivity bounds (`V_i > 0`, `0 <= Sigma_i <= 1`)
  - causality-locality (updates use local neighborhood only)
- Not conserved:
  - `|N|`, `V_tot`
- Explicitly postponed:
  - full continuity equation for `chi`-flux (reserved for future v2 if needed)

## 7) Mathematical Closure Gates

The closure is accepted only if all gates pass:

1. Dimensional consistency:
  - `V_0` contributes as `L^3`, `a(t)` dimensionless.
2. GR limit sanity:
  - under `tau -> 0` and coarse-grain, no runaway acceleration from volume update alone.
3. Identifiability:
  - `tau` and `chi` are inferable from data with non-degenerate mapping (`tau = alpha_tau * chi`).

## 8) Test Suite Attached to This Closure

- `T-V-01`: conservation/growth gate (`V_tot` or `|N|` trend, depending on rule).
- `T-V-02`: stationary spectrum gate for `P(V_i)` after burn-in.
- `T-V-03`: attractor/identity robustness under perturbations.
- `T-V-04`: GR-limit kill switch (no unphysical acceleration blow-up as `tau -> 0`).

These are executed by `scripts/run_qng_t_v_volume_rules.py`.

