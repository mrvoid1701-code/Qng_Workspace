# QNG-C-112 Derivation

- Claim statement: Inflation is replaced by a coherence-burst mechanism with rapid global synchronization.
- Source page(s): page-077
- Claim status/confidence: predicted / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
R(t) = |(1/|N|) * sum_i exp(i*phi_i)|
dR/dt = gamma_sync*R*(1-R) - gamma_dec*R
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Inflation is replaced by a coherence-burst mechanism with rapid global synchronization.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Coherence-burst acts as a synchronization mechanism; quantify burst width and amplitude in simulations.

## Next Action

- Link QNG-C-112 to 05_validation/test-plan.md with explicit dataset and threshold.
