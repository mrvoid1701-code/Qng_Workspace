# QNG-C-072 Derivation

- Claim statement: Example estimate gives chi about 2.33e-7 s kg per m for m = 70 kg.
- Source page(s): page-052
- Claim status/confidence: derived / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
chi = 70/(3e8) = 2.33e-7 kg*s/m
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Example estimate gives chi about 2.33e-7 s kg per m for m = 70 kg.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-072 to 05_validation/test-plan.md with explicit dataset and threshold.
