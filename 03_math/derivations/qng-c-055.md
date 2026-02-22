# QNG-C-055 Derivation

- Claim statement: Directional anomaly magnitude depends on velocity orientation relative to field gradients.
- Source page(s): page-036,page-037,page-044
- Claim status/confidence: predicted / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
|a_res| ~ tau*|v|*|partial_parallel nablaSigma|
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Directional anomaly magnitude depends on velocity orientation relative to field gradients.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-055 to 05_validation/test-plan.md with explicit dataset and threshold.
