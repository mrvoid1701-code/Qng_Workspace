# QNG-C-056 Derivation

- Claim statement: Unified gravity-memory equation recovers classical gravity in tau to zero limit.
- Source page(s): page-037
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
tau->0 => a_total = -nablaSigma
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Unified gravity-memory equation recovers classical gravity in tau to zero limit.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- This is the key reduction used to recover Newton/GR-like behavior.

## Next Action

- Link QNG-C-056 to 05_validation/test-plan.md with explicit dataset and threshold.
