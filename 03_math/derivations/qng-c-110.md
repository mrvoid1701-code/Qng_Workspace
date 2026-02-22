# QNG-C-110 Derivation

- Claim statement: Early-universe anomalies predicted include non-Gaussianity, cold spots, and axis-alignment remnants.
- Source page(s): page-076
- Claim status/confidence: predicted / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
DeltaT/T = (DeltaT/T)_G + epsilon_coh * M(n_hat)
Non-Gaussian marker: f_NL_eff != 0; axis marker: A_axis != 0
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Early-universe anomalies predicted include non-Gaussianity, cold spots, and axis-alignment remnants.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Prediction targets summary statistics (f_NL, cold-spot significance, axis alignment), not a single map feature.

## Next Action

- Link QNG-C-110 to 05_validation/test-plan.md with explicit dataset and threshold.
