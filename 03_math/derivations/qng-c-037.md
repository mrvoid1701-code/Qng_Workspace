# QNG-C-037 Derivation

- Claim statement: Stability memory field follows convolution Sigma(x,t) = integral K(t-t') chi(x,t') dt'.
- Source page(s): page-029,page-035,page-060
- Claim status/confidence: formalized / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Sigma(x,t) = integral_{-inf}^{t} K(t-t')*chi(x,t') dt'
K(Delta t)=(1/tau)exp(-Delta t/tau)
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Stability memory field follows convolution Sigma(x,t) = integral K(t-t') chi(x,t') dt'.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-037 to 05_validation/test-plan.md with explicit dataset and threshold.
