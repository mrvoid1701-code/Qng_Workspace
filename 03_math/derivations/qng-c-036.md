# QNG-C-036 Derivation

- Claim statement: Emergent gravity force follows F_grav = minus gradient of Sigma.
- Source page(s): page-028,page-035,page-073
- Claim status/confidence: formalized / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
g(x,t) = -nablaSigma(x,t)
F_grav = m_test * g
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Emergent gravity force follows F_grav = minus gradient of Sigma.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-036 to 05_validation/test-plan.md with explicit dataset and threshold.
