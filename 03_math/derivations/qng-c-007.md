# QNG-C-007 Derivation

- Claim statement: The node state is the triple N_i = (V_i, chi_i, phi_i).
- Source page(s): page-019,page-071
- Claim status/confidence: formalized / high
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
N_i = (V_i, chi_i, phi_i)
N_i(t+1) = U(N_i(t), neighbors, eta_i(t))
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- The node state is the triple N_i = (V_i, chi_i, phi_i).
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-007 to 05_validation/test-plan.md with explicit dataset and threshold.
