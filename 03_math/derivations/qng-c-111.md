# QNG-C-111 Derivation

- Claim statement: Time arrow is irreversible update ordering and entropy scales with count of stable reconfigurations.
- Source page(s): page-077
- Claim status/confidence: derived / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
S(t) = k_S * log(Omega(t))
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Time arrow is irreversible update ordering and entropy scales with count of stable reconfigurations.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-111 to 05_validation/test-plan.md with explicit dataset and threshold.
