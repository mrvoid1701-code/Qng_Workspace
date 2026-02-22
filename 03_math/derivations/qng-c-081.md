# QNG-C-081 Derivation

- Claim statement: Einstein equation can be extended with delayed-response tensor T_chi to encode memory curvature.
- Source page(s): page-060
- Claim status/confidence: derived / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
G^{mu nu} = 8*pi*G_N*(T_matter^{mu nu} + T_chi^{mu nu})
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Einstein equation can be extended with delayed-response tensor T_chi to encode memory curvature.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- T_chi^{mu nu} must preserve total covariant conservation constraints.

## Next Action

- Link QNG-C-081 to 05_validation/test-plan.md with explicit dataset and threshold.
