# QNG-C-118

- Status: testable
- Confidence: high
- Source page(s): page-084
- Related derivation: 03_math/derivations/qng-c-118.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Falsification criteria include failure to fit tau-lag data, absent Sigma-lag lensing, and failed GR recovery in nodal simulations.

## Assumptions

- Falsification must be binary, pre-registered, and resistant to post-hoc threshold changes.
- Three independent failure gates are sufficient: tau-lag fit, Sigma-lag lensing, and GR-limit recovery.
- A single hard failure is enough to invalidate the current QNG variant.

## Mathematical Form

- `F = 1[g_taufail or g_lensfail or g_GRfail]`
- `QNG variant accepted only if F = 0`

## Potential Falsifier

- Any replicated gate failure (`g_taufail=1`, `g_lensfail=1`, or `g_GRfail=1`) falsifies the claimed variant.

## Evidence / Notes

- Lensing gate has strong support from current gold results, while tau-lag and GR-limit gates still need full production closure.
- Linked derivation: `03_math/derivations/qng-c-118.md`.

## Next Action

- Freeze gate definitions and thresholds in `05_validation/test-plan.md`, then execute remaining gate tests with negative controls and replication.

