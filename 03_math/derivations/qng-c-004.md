# QNG-C-004 Derivation

- Claim statement: A node persists only when Sigma_i is at or above Sigma_min.
- Source page(s): page-016,page-028
- Claim status/confidence: formalized / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
persist_i(t+1) = H(Sigma_i(t) - Sigma_min)
Node exists <=> Sigma_i >= Sigma_min
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- A node persists only when Sigma_i is at or above Sigma_min.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-004 to 05_validation/test-plan.md with explicit dataset and threshold.
