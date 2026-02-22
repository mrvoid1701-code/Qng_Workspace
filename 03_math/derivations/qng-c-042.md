# QNG-C-042 Derivation

- Claim statement: Mass is proportional to temporal stability Sigma_temp.
- Source page(s): page-031,page-073
- Claim status/confidence: formalized / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
m = m_0 * Sigma_temp
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Mass is proportional to temporal stability Sigma_temp.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-042 to 05_validation/test-plan.md with explicit dataset and threshold.
