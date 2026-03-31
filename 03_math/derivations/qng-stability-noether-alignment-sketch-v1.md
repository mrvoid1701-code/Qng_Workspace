# QNG Stability Noether/Action Alignment (Sketch v1)

Date: 2026-03-03  
Scope: proof sketch (not full theorem)

## 1) Setup

Discrete action (frozen in stability-v1 docs):

- `S = sum_t L_t`
- `L_t = sum_i [ T_i - V_i ]`
- `V_i` is the local potential used by the stress runner.
- `T_i` is discrete kinetic/update contribution induced by `(Sigma, chi, phi)` increments.

The implemented one-step update is an explicit discrete Euler-Lagrange-like step with:

- projected `Sigma` update (`clip` to enforce bounds),
- local `chi` and `phi` updates,
- optional stochastic forcing (noise).

## 2) Why `E_gate` drifts while `E_noether` is the aligned observable

`E_gate` uses only potential-like energy snapshot:

- `E_gate(t) = V(Sigma_t, chi_t, phi_t)`.

For a gradient-flow-like dissipative update, `V` alone is not expected to be conserved.
Therefore `|Delta E_gate / E_gate|` can show secular drift even when the update is
well-behaved variationally.

The aligned discrete Noether-like track augments with accumulated discrete dissipation:

- `E_noether(t) = V_t + D_t`,
- `D_t = sum_{k<t} Q_k`,
- `Q_k >= 0` built from squared local update gradients.

Under the same frozen update rule, this `E_noether` is the observable that tracks the
discrete action balance (up to projection/noise residuals), so it is the correct
stability-facing energy proxy for decision gating.

## 3) Residual term and bounded error

Let `r_k` denote the per-step variational residual from:

1. `Sigma` projection to `[0,1]`,
2. stochastic forcing in `chi/phi`,
3. explicit time discretization error.

Then, schematically:

- `E_noether(t+1) - E_noether(t) = O(r_t)`.

If residual gate stays bounded (`max_residual <= threshold`), accumulated mismatch stays
bounded and does not induce runaway in the official energy decision.

## 4) Practical implication for gates

1. Keep non-energy gates unchanged (boundedness, metric positivity/conditioning, runaway, residual, alpha-drift, locality).
2. Use Noether-like drift for official energy decision (`v2`).
3. Keep `v1` energy as legacy diagnostic to preserve comparability and detect pathological cases.

## 5) Limitations of this sketch

This note is not a full formal proof. Missing pieces:

1. rigorous coercivity/Lipschitz constants for all discrete operators,
2. full stochastic stability bound with explicit high-probability constants,
3. continuum-limit theorem tying `h, dt, epsilon` jointly.
