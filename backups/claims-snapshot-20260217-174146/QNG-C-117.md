# QNG-C-117

- Status: testable
- Confidence: high
- Source page(s): page-085
- Related derivation: 03_math/derivations/qng-c-117.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Priority tests target flyby lag, dark-sector lensing, CMB coherence, and structure datasets.

## Assumptions

- A small set of priority tests can cover the highest-leverage falsifiable predictions of the framework.
- Each test produces a comparable normalized score with pre-registered thresholds.
- Combined status can be tracked by a weighted scorecard without replacing per-test pass/fail gates.

## Mathematical Form

- `Z_total = sum_i w_i * z_i`
- `Priority pass set: z_flyby < z0, z_lensing < z0, z_cmb < z0, z_lss < z0`

## Potential Falsifier

- If one or more priority tests repeatedly fail pre-registered criteria under independent reruns, the priority-test claim is falsified.

## Evidence / Notes

- Dark-sector lensing branch already has gold passes (`QNG-T-027`, `QNG-T-039`); other branches remain active.
- Linked derivation: `03_math/derivations/qng-c-117.md`.

## Next Action

- Maintain a single mission scoreboard for flyby, lensing, CMB, and structure tests with frozen thresholds and cadence.

