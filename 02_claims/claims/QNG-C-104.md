# QNG-C-104

- Status: derived
- Confidence: low
- Source page(s): page-075
- Related derivation: 03_math/derivations/qng-c-104.md
- Closure reference: 01_notes/core-closure-v1.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The emergent scale factor follows cube-root scaling with stable node count as a controlled approximation:

```text
a(t) ~= (N_s(t)/N_s(t0))^(1/3)
```

when mean node volume drift is small.

## Assumptions

- A1. `a(t)` is defined from relational volume, not background metric.
- A2. `V_tot = N_s * V_bar`.
- A3. The approximation is valid when `V_bar` changes slowly.
- A4. Node proliferation is stability-gated (`Sigma_i >= Sigma_min`).
- A5. Coarse-grained isotropy is used for scalar `a(t)` interpretation.

## Mathematical Form

- Exact factorization:
  - `a(t) = [N_s(t)/N_s(t0)]^(1/3) * [V_bar(t)/V_bar(t0)]^(1/3)`
- Approximation gate:
  - `|d ln(V_bar)/dt| << |d ln(N_s)/dt|`

## Potential Falsifier

- Persistent large correction from `V_bar` drift invalidates cube-root approximation.
- Poor fit of `a_obs` to cube-root relation across robust runs.
- Relation holds only under unstable or overfit parameter sets.

## Evidence / Notes

- Claim now includes explicit correction factor, reducing over-claiming risk.
- Supports direct approximation-quality metrics (`R^2`, drift ratios).

## Next Action

- Run and evaluate:
  - `T-V-02` spectrum/drift gate
  - `T-V-04` GR-limit sanity gate
