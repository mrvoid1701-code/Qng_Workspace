# QNG-C-032

- Status: formalized
- Confidence: high
- Source page(s): page-028,page-072
- Related derivation: 03_math/derivations/qng-c-032.md
- Closure reference: 01_notes/core-closure-v1.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Node stability is a bounded scalar:

```text
Sigma_i = Sigma_chi,i * Sigma_struct,i * Sigma_temp,i * Sigma_phi,i
0 <= Sigma_i <= 1
```

and node persistence is controlled by `Sigma_i >= Sigma_min`.

## Assumptions

- A1. Stability is multi-factor, not single-factor.
- A2. Component terms are dimensionless and bounded.
- A3. Multiplicative closure is adequate in v1.
- A4. `tau_i = alpha_tau * chi_i` links temporal stability to `chi`.
- A5. Structural term depends on quantized volume state (`k_i`).

## Mathematical Form

- Example bounded component closure:
  - `Sigma_chi,i = exp(-|chi_i-chi_ref|/chi_ref)`
  - `Sigma_struct,i = exp(-|k_i-k_eq|/k_eq)`
  - `Sigma_temp,i = exp(-|Delta_t_local-tau_i|/tau_i)`
  - `Sigma_phi,i = (1+cos(Delta_phi_i))/2`

## Potential Falsifier

- A required stability function outside `[0,1]`.
- Persistent mismatch between `Sigma` gates and node persistence behavior.
- Failure of stationary/attractor gates when applied to closure v1.

## Evidence / Notes

- Bounded multiplicative structure now has explicit, dimensionally consistent component maps.
- Supports direct testing of spectrum stationarity and attractor robustness.

## Next Action

- Execute and track:
  - `T-V-02` stationary spectrum gate
  - `T-V-03` attractor/identity gate
