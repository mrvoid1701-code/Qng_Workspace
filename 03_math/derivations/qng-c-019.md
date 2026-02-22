# QNG-C-019 Derivation

- Claim statement: Distance is graph shortest-path length and curvature is encoded topologically.
- Source page(s): page-020
- Claim status/confidence: derived / medium
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
kappa_i ~ avg_{j in Adj(i)}(k_j) - k_i
Curvature proxy from graph-topology imbalance
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Distance is graph shortest-path length and curvature is encoded topologically.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Next Action

- Link QNG-C-019 to 05_validation/test-plan.md with explicit dataset and threshold.
