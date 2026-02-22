# QNG-C-114

- Status: speculative
- Confidence: low
- Source page(s): page-079,page-080
- Related derivation: 03_math/derivations/qng-c-114.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Engineering tau may delay or accelerate effective information transfer and temporal response.

## Assumptions

- Composite time response follows `T_C = t_R + v*tau` at first order.
- `tau` can be tuned or perturbed in a controlled environment without confounding geometry changes.
- Timing instrumentation resolves `Delta T_C` at the required scale.

## Mathematical Form

- `T_C = t_R + v * tau`
- `Delta T_C = v * Delta tau`

## Potential Falsifier

- If engineered `Delta tau` fails to induce reproducible `Delta T_C` across repeated directional protocols, the claim is falsified.

## Evidence / Notes

- This is a controllability hypothesis and should be treated separately from signal-propagation speed claims.
- Linked derivation: `03_math/derivations/qng-c-114.md`.

## Next Action

- Build a timing test matrix with direction/velocity sweeps and null-control conditions to estimate `dT_C/dtau`.

