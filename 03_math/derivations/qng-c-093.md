# QNG-C-093 Derivation

- Claim statement: GR emerges as a macroscopic limit when tau approaches zero and updates appear continuous.
- Source page(s): page-047,page-067
- Claim status/confidence: derived / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
a_total = -nablaSigma - tau*(v.nabla)nablaSigma + O(tau^2)
tau->0 => classical limit
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- GR emerges as a macroscopic limit when tau approaches zero and updates appear continuous.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-093 to 05_validation/test-plan.md with explicit dataset and threshold.
