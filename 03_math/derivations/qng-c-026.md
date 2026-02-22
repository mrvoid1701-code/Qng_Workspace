# QNG-C-026 Derivation

- Claim statement: Pioneer and flyby anomalies are first-order consequences of lag dynamics.
- Source page(s): page-025,page-044,page-063
- Claim status/confidence: predicted / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
a_res ~ -tau * (v . nabla) nablaSigma
Flyby/Pioneer residual follows first-order lag term
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Pioneer and flyby anomalies are first-order consequences of lag dynamics.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Same operator as QNG-C-025, applied to mission-specific trajectories.

## Next Action

- Link QNG-C-026 to 05_validation/test-plan.md with explicit dataset and threshold.
