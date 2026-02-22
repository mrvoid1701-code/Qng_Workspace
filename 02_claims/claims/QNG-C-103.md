# QNG-C-103

- Status: predicted
- Confidence: low
- Source page(s): page-075
- Related derivation: 03_math/derivations/qng-c-103.md
- Closure reference: 01_notes/core-closure-v1.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Cosmic expansion emerges from proliferation of stable nodes and growth of relational complexity under the frozen v1 volume rule.

## Assumptions

- A1. Geometry is relational (`G=(N,E)`), not predefined metric embedding.
- A2. Expansion proxy is `a(t)=(V_tot/V_tot0)^(1/3)`.
- A3. v1 uses expansive volume rule (V-B): births and local `k_i` growth can increase `V_tot`.
- A4. Stable nodes are selected by `Sigma_i >= Sigma_min`.
- A5. Complexity co-growth (`C(t)`) is expected in expansion regimes.

## Mathematical Form

- `V_tot(t+1)-V_tot(t) = V_0*(sum Delta_k_i^+ - sum Delta_k_i^- + N_birth - N_death)`
- Expansion regime condition:
  - `E[Delta V_tot] > 0`
  - `da/dt > 0`

## Potential Falsifier

- No positive `V_tot` or `N_s` drift under frozen v1 in robust seed runs.
- Complexity decouples or anti-correlates from expansion proxy.
- Growth only appears under unstable/explosive parameter settings.

## Evidence / Notes

- Claim is mapped to explicit growth and robustness gates (`T-V-01`, `T-V-02`).
- This framing separates expansion as measurable behavior, not narrative interpretation.

## Next Action

- Run and evaluate:
  - `T-V-01` conservation/growth gate
  - `T-V-02` stationarity/drift gate
