# QNG-C-118 Derivation

- Claim statement: Falsification criteria include failure to fit tau-lag data, absent Sigma-lag lensing, and failed GR recovery in nodal simulations.
- Source page(s): page-084
- Claim status/confidence: testable / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Falsify if any gate fails: F = 1[g_taufail or g_lensfail or g_GRfail]
QNG valid only if F = 0
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Falsification criteria include failure to fit tau-lag data, absent Sigma-lag lensing, and failed GR recovery in nodal simulations.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Falsification logic should remain binary and pre-registered to avoid post-hoc threshold tuning.

## Next Action

- Link QNG-C-118 to 05_validation/test-plan.md with explicit dataset and threshold.
