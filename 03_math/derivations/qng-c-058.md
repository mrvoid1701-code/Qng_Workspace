# QNG-C-058 Derivation

- Claim statement: Lensing traces gradient Sigma and can be offset from baryonic mass centers.
- Source page(s): page-039,page-060,page-064
- Claim status/confidence: predicted / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Phi_lens ~ Sigma
alpha_hat ~ nabla_perp Phi_lens ~ nabla_perp Sigma
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Lensing traces gradient Sigma and can be offset from baryonic mass centers.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-058 to 05_validation/test-plan.md with explicit dataset and threshold.
