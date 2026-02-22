# QNG-C-062 Derivation

- Claim statement: N-body simulations with memory kernels should reproduce QNG-consistent structure signatures.
- Source page(s): page-040,page-084
- Claim status/confidence: predicted / low
- Math maturity: v1

## Definitions

- Sigma: stability field scalar.
- chi: straton load (chi = m/c).
- tau: relaxation/memory delay.
- nabla: spatial gradient operator.

## Equations

```text
Sigma^n = sum_{m<=n} w_{n-m}*chi^m, w_r~exp(-r*dt/tau)
a_k^n = -nablaSigma^n(x_k^n)
```

## Derivation Steps

1. Start from the canonical QNG definitions used in this claim.
2. Substitute chi/tau/Sigma relationships from source pages.
3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.
4. Keep only terms required for the claim-level observable.

## Result

- N-body simulations with memory kernels should reproduce QNG-consistent structure signatures.
- The equations above are the operational form to carry into validation/tests.

## Checks

- Verify dimensional consistency after selecting model calibration constants.
- Verify sign convention against g = -nablaSigma definition.
- Compare limiting behavior as tau -> 0.

## Claim-Specific Notes

- Use the same kernel tau as observational fits for consistency checks.

## Next Action

- Link QNG-C-062 to 05_validation/test-plan.md with explicit dataset and threshold.
