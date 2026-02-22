# QNG-C-103 Derivation

- Claim statement: Cosmic expansion corresponds to proliferation of stable nodes and relational complexity.
- Source page(s): `page-075`
- Claim status/confidence: `predicted / low`
- Math maturity: `v2 (volume-rule closure)`
- Closure note: `01_notes/core-closure-v1.md`

## Definitions

- Stable node count:
  - `N_s(t) = |{ i : Sigma_i(t) >= Sigma_min }|`
- Total relational volume:
  - `V_tot(t) = sum_{i in N_s(t)} V_i(t)`
- Effective scale factor:
  - `a(t) = (V_tot(t) / V_tot(t0))^(1/3)`
- Complexity proxy:
  - `C(t) = |E(t)| / max(N_s(t), 1)`

## Expansion Under Frozen V-B Rule

Birth/death plus quantized growth imply:

```text
V_tot(t+1) - V_tot(t) = V_0 * (sum_i Delta_k_i^+ - sum_i Delta_k_i^- + N_birth - N_death)
```

In expansion regime (coherent/high-stability epochs):

```text
E[V_tot(t+1) - V_tot(t)] > 0
=> da/dt > 0
```

Complexity coupling condition:

```text
dC/dt > 0 when dN_s/dt > 0 under persistent local coherence
```

## Derivation Steps

1. Define expansion from relational volume, not background metric.
2. Substitute `V_i = k_i V_0` and birth/death gates from `C-029`.
3. Aggregate local updates to derive `Delta V_tot`.
4. Show positive-drift regime under frozen V-B rule.
5. Link positive `Delta V_tot` to `a(t)` growth.

## Result

- `C-103` reduces to measurable simulation gates:
  - positive trend in `N_s(t)` and/or `V_tot(t)`,
  - positive expansion `a(t)`,
  - co-growth in complexity.

## Checks

- Dimensional:
  - `a(t)` is dimensionless by construction.
- Consistency:
  - no expansion claim without node/volume positive drift.
- Robustness:
  - trend must persist across seed variations (not one trajectory).

## Next Action

- Validate with:
  - `T-V-01` conservation/growth gate
  - `T-V-02` spectrum drift/stationarity characterization

