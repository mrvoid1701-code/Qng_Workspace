# QNG-C-077 Derivation

- Claim statement: Causality is defined by state-dependency edges in the update graph.
- Source page(s): page-056
- Claim status/confidence: formalized / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
e_a <= e_b if dependency path exists from e_a to e_b
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Causality is defined by state-dependency edges in the update graph.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-077 to 05_validation/test-plan.md with explicit dataset and threshold.
