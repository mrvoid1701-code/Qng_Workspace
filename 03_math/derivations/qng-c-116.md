# QNG-C-116 Derivation

- Claim statement: QNG resonators and nodal-update encoding suggest programmable physics and topology-based computation.
- Source page(s): page-080,page-081
- Claim status/confidence: speculative / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
N(t+1) = U_theta(N(t))
Resonance condition: arg(lambda_k(U_theta)) = 2*pi*m/T
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- QNG resonators and nodal-update encoding suggest programmable physics and topology-based computation.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Programmable-physics interpretation requires a reproducible control map theta -> U_theta and error bounds.

## Next Action

- Link QNG-C-116 to 05_validation/test-plan.md with explicit dataset and threshold.
