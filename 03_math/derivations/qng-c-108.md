# QNG-C-108 Derivation

- Claim statement: Filaments are phase-stable corridors where directional coherence survives and tau is low.
- Source page(s): page-076
- Claim status/confidence: predicted / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
C_phi(x,t) = |<exp(i*phi)>_local|
Filament corridor: C_phi >= C_min and tau(x,t) <= tau_max
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Filaments are phase-stable corridors where directional coherence survives and tau is low.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Corridor criterion is operational and should be calibrated against filament catalogs.

## Next Action

- Link QNG-C-108 to 05_validation/test-plan.md with explicit dataset and threshold.
