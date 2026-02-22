# QNG-C-113 Derivation

- Claim statement: Since m = c times chi, engineering local chi could produce effective mass engineering.
- Source page(s): page-079
- Claim status/confidence: speculative / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
m_eff(x) = c * chi(x)
Delta m_eff = c * Delta chi
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Since m = c times chi, engineering local chi could produce effective mass engineering.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Speculative engineering claim; include explicit control-energy and stability-cost terms before hardware interpretation.

## Next Action

- Link QNG-C-113 to 05_validation/test-plan.md with explicit dataset and threshold.
