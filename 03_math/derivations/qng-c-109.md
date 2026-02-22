# QNG-C-109 Derivation

- Claim statement: Apparent cosmic acceleration can emerge from update-rate change and global desynchronization.
- Source page(s): page-076,page-077
- Claim status/confidence: predicted / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
H_obs(t) = H_geom(t) + d/dt[ln U(t)] - d/dt[ln C_sync(t)]
q_obs = -1 - (dH_obs/dt)/H_obs^2
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- Apparent cosmic acceleration can emerge from update-rate change and global desynchronization.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Acceleration claim is effective/phenomenological and does not assume Lambda by construction.

## Next Action

- Link QNG-C-109 to 05_validation/test-plan.md with explicit dataset and threshold.
