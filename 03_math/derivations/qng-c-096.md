# QNG-C-096 Derivation

- Claim statement: QFT-like dynamics emerge from coherent node excitations with Klein-Gordon-type propagation.
- Source page(s): page-068
- Claim status/confidence: derived / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Phi(x,t)=sum_i phi_i(t) delta(x-x_i)
Box Phi + V'(Phi)=0 (effective)
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- QFT-like dynamics emerge from coherent node excitations with Klein-Gordon-type propagation.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Continuum form is valid only after coarse graining of node excitations.

## Next Action

- Link QNG-C-096 to 05_validation/test-plan.md with explicit dataset and threshold.
