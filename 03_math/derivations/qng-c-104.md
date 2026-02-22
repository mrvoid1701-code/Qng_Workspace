# QNG-C-104 Derivation

- Claim statement: Emergent scale factor follows cube-root scaling with node count.
- Source page(s): `page-075`
- Claim status/confidence: `derived / low`
- Math maturity: `v2 (volume-rule closure)`
- Closure note: `01_notes/core-closure-v1.md`

## Definitions

- Effective scale factor:
  - `a(t) = (V_tot(t) / V_tot(t0))^(1/3)`
- Total relational volume:
  - `V_tot(t) = sum_i V_i(t)`
- Mean node volume:
  - `V_bar(t) = V_tot(t) / N_s(t)`

## Core Relation

Exact decomposition:

```text
a(t) = [N_s(t) / N_s(t0)]^(1/3) * [V_bar(t) / V_bar(t0)]^(1/3)
```

Cube-root node-count law is recovered when mean node volume drift is small:

```text
|d ln(V_bar)/dt| << |d ln(N_s)/dt|
=> a(t) ~= [N_s(t)/N_s(t0)]^(1/3)
```

## Derivation Steps

1. Start from volumetric definition of `a(t)`.
2. Factor `V_tot = N_s * V_bar`.
3. Take ratio to initial time `t0`.
4. Identify correction term from `V_bar` drift.
5. State cube-root as first-order closure valid in quasi-stationary `V_bar` regime.

## Result

- `C-104` is valid as a controlled approximation, with an explicit correction factor.
- This avoids over-claiming a universal exact law.

## Checks

- Dimensional consistency:
  - all ratios are dimensionless.
- Identifiability:
  - separate `N_s` and `V_bar` contributions to avoid degeneracy.
- Robustness:
  - check law under seed splits and perturbations.

## Next Action

- Validate with:
  - `T-V-02` stationary spectrum gate (for `V_bar` drift control)
  - `T-V-04` GR-limit sanity gate

