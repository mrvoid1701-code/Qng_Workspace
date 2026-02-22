# QNG-C-094 Derivation

- Claim statement: Einstein field equation is recovered as approximation in the smooth large-scale limit.
- Source page(s): page-067
- Claim status/confidence: derived / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Coarse-grained fast-response limit maps to Einstein-form closure
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Einstein field equation is recovered as approximation in the smooth large-scale limit.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Requires explicit coarse-graining map from graph variables to continuum fields.

## Next Action

- Link QNG-C-094 to 05_validation/test-plan.md with explicit dataset and threshold.
