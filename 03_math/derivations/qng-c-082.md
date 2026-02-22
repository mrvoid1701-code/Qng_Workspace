# QNG-C-082 Derivation

- Claim statement: Rotation-curve excess can be explained by historical Sigma lag from prior mass distributions.
- Source page(s): page-060,page-064
- Claim status/confidence: predicted / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
v_c(r)^2/r = g_baryon(r) + g_memory(r)
g_memory(r) = -partial_r Sigma_memory(r)
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Rotation-curve excess can be explained by historical Sigma lag from prior mass distributions.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-082 to 05_validation/test-plan.md with explicit dataset and threshold.
