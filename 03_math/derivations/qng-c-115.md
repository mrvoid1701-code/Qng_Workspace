# QNG-C-115 Derivation

- Claim statement: Artificial stability gradients may lens light or particles for sensing and communication.
- Source page(s): page-080
- Claim status/confidence: speculative / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
g_art(x,t) = -nablaSigma_art(x,t)
alpha_hat_art ~ (2/c^2) * integral g_art,perp dl
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Artificial stability gradients may lens light or particles for sensing and communication.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Lensing analogue should be benchmarked first in simulation/graph-lab setups before astrophysical scaling.

## Next Action

- Link QNG-C-115 to 05_validation/test-plan.md with explicit dataset and threshold.
