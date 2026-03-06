# QNG Stability - Discrete to Continuum Convergence Rate (v1)

- Date: 2026-03-06
- Status: formal contract with explicit rate terms
- Scope: `Sigma, chi, phi` lane under graph coarse-graining
- Purpose: convert "trend-only" convergence into an explicit error model

## 1) Objects

Let `U_h^n` be the discrete state at level `h` (node spacing proxy), time index `n`, step `Delta t`.

Let `u(t,x)` be the target continuum solution on `[0,T]`.

Let `I_h` be the interpolation/coarse-graining operator from graph to continuum fields.

Define error:

```text
e_h^n = || I_h U_h^n - u(t_n) ||_X
```

for a fixed normed space `X` (`L2` or `Linf` contract must be declared per test).

## 2) Assumptions (Preregisterable)

1. Regularity:
   - continuum solution has enough smoothness (at least `C^{p+1}` in space, `C^2` in time).
2. Consistency:
   - one-step local truncation error obeys
     `||tau_h^n||_X <= C_h h^p + C_t (Delta t)^2 + C_k eps_k + C_m xi_M`.
3. Stability:
   - one-step propagator is Lipschitz:
     `||Phi_h(a)-Phi_h(b)||_X <= (1 + L Delta t) ||a-b||_X`.
4. Interpolation bias:
   - `||I_h u_h^0 - u(0)||_X <= C_0 h^p`.

Here:

- `h`: graph resolution scale proxy,
- `p`: spatial order (empirical lane usually targets `p in [1,2]`),
- `eps_k`: kernel/coarse-graining mismatch term,
- `xi_M`: finite-sample graph term (typically `~ M^(-1/2)` up to logs).

## 3) Discrete Error Recurrence

From consistency + stability:

```text
e_h^{n+1} <= (1 + L Delta t) e_h^n + C_h h^p + C_t (Delta t)^2 + C_k eps_k + C_m xi_M.
```

Applying discrete Gronwall on `n <= T/Delta t`:

```text
e_h^n <= exp(L t_n) * (
  e_h^0
  + t_n * [ C_h h^p + C_t Delta t + C_k eps_k + C_m xi_M ]
).
```

Therefore, for fixed `T`:

```text
sup_{n: t_n<=T} e_h^n
<= C(T) * ( h^p + Delta t + eps_k + xi_M ).
```

This is the explicit rate contract.

## 4) Practical Parametrization

For stochastic graph sampling with `M` nodes:

```text
xi_M = sqrt(log(M) / M)
```

is a standard conservative choice.

So an operational bound is:

```text
sup e_h^n <= C(T) * ( h^p + Delta t + eps_k + sqrt(log(M)/M) ).
```

## 5) Mapping to Existing Convergence Lane

Current convergence governance (`v6`) already tracks cross-level trend behavior.
This note upgrades interpretation:

1. trend pass is evidence that the RHS terms decrease with refinement,
2. failure can be attributed to one (or more) explicit terms:
   - spatial resolution term `h^p`,
   - temporal term `Delta t`,
   - kernel mismatch `eps_k`,
   - finite-sample term `xi_M`.

## 6) Required Reporting for Rate Claims

When claiming convergence rate in evidence:

1. report tested level set `(h_1,...,h_K)` and `Delta t`,
2. report observed slope proxy and confidence interval,
3. report estimated `xi_M` term per level,
4. state whether claim is:
   - deterministic rate (noise-off), or
   - statistical rate (noise-on, high-probability).

Without these four items, only "empirical trend" can be claimed, not a rate.

## 7) Limitations

1. Constants `C_h, C_t, C_k, C_m, L` are not yet closed-form calibrated.
2. In multi-peak/sparse regimes, `eps_k` and `xi_M` may dominate.
3. This is a conditional theorem contract, not a complete PDE-limit proof.
