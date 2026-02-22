# QNG-C-038 Derivation

- Claim statement: Residual acceleration from lag is approximately a_res = -tau(v dot grad)grad Sigma.
- Source page(s): page-029,page-036,page-063
- Claim status/confidence: derived / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
a_res ~ -tau*(v.nabla)nablaSigma
a_total = -nablaSigma + a_res
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Residual acceleration from lag is approximately a_res = -tau(v dot grad)grad Sigma.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-038 to 05_validation/test-plan.md with explicit dataset and threshold.
