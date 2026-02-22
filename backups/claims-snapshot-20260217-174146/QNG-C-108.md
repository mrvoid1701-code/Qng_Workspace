# QNG-C-108

- Status: predicted
- Confidence: low
- Source page(s): page-076
- Related derivation: 03_math/derivations/qng-c-108.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Filaments are phase-stable corridors where directional coherence survives and tau is low.

## Assumptions

- Local phase coherence can be estimated by a stable statistic on filament neighborhoods.
- Filament regions correspond to persistent high-coherence corridors in the QNG graph.
- Effective delay field `tau(x,t)` is lower in these corridors than in nearby void-like regions.

## Mathematical Form

- `C_phi(x,t) = |<exp(i*phi)>_local|`
- `Filament corridor criterion: C_phi(x,t) >= C_min and tau(x,t) <= tau_max`

## Potential Falsifier

- If observed large-scale filaments do not show elevated coherence proxies or do not correlate with low-delay regions relative to controls, the claim is falsified.

## Evidence / Notes

- Claim is predictive and currently model-driven; direct observational proxy mapping is still pending.
- Linked derivation: `03_math/derivations/qng-c-108.md`.

## Next Action

- Define operational estimators for `C_phi` and `tau` on simulation outputs, then test correlation on filament catalogs vs matched non-filament controls.

