# QNG-C-040 Derivation

- Claim statement: Dark halos are time-dependent and can dissipate through long-term relaxation.
- Source page(s): page-029,page-037,page-040,page-061
- Claim status/confidence: predicted / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
d(DeltaSigma_DM)/dt = -(1/tau_h)DeltaSigma_DM + source
source=0 => DeltaSigma_DM~exp(-t/tau_h)
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Dark halos are time-dependent and can dissipate through long-term relaxation.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Predicts measurable halo fading timescale tau_h in isolated systems.

## Next Action

- Link QNG-C-040 to 05_validation/test-plan.md with explicit dataset and threshold.
