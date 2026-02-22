# QNG-C-117 Derivation

- Claim statement: Priority tests target flyby lag, dark-sector lensing, CMB coherence, and structure datasets.
- Source page(s): page-085
- Claim status/confidence: testable / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Z_total = sum_i w_i * z_i
Pass set: z_flyby<z0, z_lensing<z0, z_cmb<z0, z_lss<z0
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Priority tests target flyby lag, dark-sector lensing, CMB coherence, and structure datasets.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Priority-test aggregator is for planning; production acceptance still uses per-test pass/fail gates.

## Next Action

- Link QNG-C-117 to 05_validation/test-plan.md with explicit dataset and threshold.
