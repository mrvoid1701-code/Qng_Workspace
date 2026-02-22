# QNG-C-027 Derivation

- Claim statement: Dark matter signal is modeled as Sigma_historical minus Sigma_instantaneous.
- Source page(s): page-024,page-029,page-036,page-059
- Claim status/confidence: formalized / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
DeltaSigma_DM = Sigma_hist - Sigma_now
Sigma(x,t) = integral K(t-t')*chi(x,t') dt'
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Dark matter signal is modeled as Sigma_historical minus Sigma_instantaneous.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-027 to 05_validation/test-plan.md with explicit dataset and threshold.
