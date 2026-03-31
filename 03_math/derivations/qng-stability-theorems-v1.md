# QNG Stability - Boundedness and Stability Theorems (v1)

- Date: 2026-03-06
- Status: formal theorem-lane note (conditional theorems)
- Scope: full `Sigma, chi, phi` update in the official stability lane
- Related implementation: `scripts/tools/run_stability_stress_v1.py::one_step`

## 1) Assumptions

Let `G=(V,E)` be finite with maximum degree `d_max < inf`.

Use fixed constants:

```text
alpha_Sigma, alpha_chi, alpha_phi > 0
k_cl, k_sm, k_chi, k_phi > 0
k_mix in R
```

Noise assumptions:

```text
E[eta_chi,i^t] = 0,  E[eta_phi,i^t] = 0
E[(eta_chi,i^t)^2] <= s_chi^2,  E[(eta_phi,i^t)^2] <= s_phi^2
```

Define:

```text
a_chi = 1 - alpha_chi * k_chi
```

and require `|a_chi| < 1` for contractive chi drift.

## 2) Theorem A (Well-Posed One-Step Map)

For every state `X^t = (Sigma^t, chi^t, phi^t)` and every noise realization, the next state
`X^{t+1}` exists and is unique.

Reason:

1. all local maps (`exp`, `sin`, `cos`, means) are continuous on finite-dimensional spaces,
2. update formulas are explicit,
3. `clip01` and `wrap` are single-valued deterministic maps.

## 3) Theorem B (State-Space Invariance)

For all `t`:

```text
Sigma_i^t in [0,1]     (all i)
phi_i^t   in (-pi,pi]  (all i)
```

Proof:

1. `Sigma^{t+1}` is obtained by `clip01`, so interval invariance is exact.
2. `phi^{t+1}` is obtained by `wrap`, so circle-chart invariance is exact.

No extra smoothness assumptions are needed.

## 4) Theorem C (First-Moment Bound for chi)

Because `Sigma in [0,1]`, we have:

```text
|Sigma_i - <Sigma>_Adj(i)| <= 1.
```

Hence the chi update satisfies:

```text
chi_i^{t+1} = a_chi * chi_i^t - alpha_chi*k_mix*DeltaSigma_i^t + eta_chi,i^t
```

with `|DeltaSigma_i^t| <= 1`. Therefore:

```text
E|chi_i^{t+1}| <= |a_chi| E|chi_i^t| + alpha_chi|k_mix| + E|eta_chi,i^t|.
```

Iterating:

```text
E|chi_i^t| <= |a_chi|^t E|chi_i^0|
            + (alpha_chi|k_mix| + sup_t E|eta_chi,i^t|) * (1 - |a_chi|^t)/(1-|a_chi|).
```

So `E|chi_i^t|` is uniformly bounded in time.

## 5) Theorem D (Second-Moment / Mean-Square Bound for chi)

Using `(x+y+z)^2 <= 3x^2 + 3y^2 + 3z^2`:

```text
E[(chi_i^{t+1})^2]
<= 3 a_chi^2 E[(chi_i^t)^2]
 + 3 alpha_chi^2 k_mix^2
 + 3 s_chi^2.
```

If `3 a_chi^2 < 1`, then:

```text
sup_t E[(chi_i^t)^2] < inf
```

with explicit bound:

```text
sup_t E[(chi_i^t)^2]
<= E[(chi_i^0)^2]
 + (3 alpha_chi^2 k_mix^2 + 3 s_chi^2)/(1 - 3a_chi^2).
```

This gives practical non-runaway control in the stochastic lane.

## 6) Theorem E (Locality / One-Step No-Signalling)

For zero-noise one-step updates, perturbing node `s` at time `t` can affect only:

```text
{s} union Adj(s)
```

at time `t+1`.

Reason:

1. each node update uses only local variables and neighbor means,
2. no two-hop terms are used in one step.

So one-step nonlocal response is exactly zero outside the 1-hop neighborhood.

## 7) Theorem F (Deterministic Descent Under Small Steps)

In the deterministic unprojected case (`eta=0`, no clip/wrap hits), let `V_t` be the lagged local potential from the EL-equivalence note. If `grad V_t` is Lipschitz with constant `L_t`, then:

```text
V_t(X^{t+1}) <= V_t(X^t) - (alpha_min - 0.5*L_t*alpha_max^2) ||grad V_t(X^t)||^2
```

where:

```text
alpha_min = min(alpha_Sigma, alpha_chi, alpha_phi)
alpha_max = max(alpha_Sigma, alpha_chi, alpha_phi).
```

Hence descent holds when:

```text
alpha_min > 0.5 * L_t * alpha_max^2.
```

With projection/noise, this becomes a bounded-drift statement (officially monitored by residual + energy gates).

## 8) Interpretation for Governance

These theorems provide:

1. guaranteed bounded domains (`Sigma`, `phi`),
2. explicit chi non-runaway conditions (`|1-alpha_chi*k_chi|<1`),
3. exact locality statement,
4. conditional descent bound.

They do not claim global asymptotic convergence of the fully non-lagged nonlinear system; that remains a higher-order theorem lane.
