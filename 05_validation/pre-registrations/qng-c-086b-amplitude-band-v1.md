# Pre-Registration: QNG-C-086b Amplitude Band v1

- Claim fragment: `C-086b` (numeric amplitude scaling for flyby/deep-space lag signal)
- Parent claim: `QNG-C-086`
- Created: `2026-02-21`
- Scope: DS-005 trajectory REAL family (`QNG-T-041` support track)
- Status: closed (falsified)

## Locked Rule Set

- Same sample policy: baseline vs memory must use identical pass rows.
- Same sigma policy: keep published uncertainty columns unchanged.
- Same likelihood policy: weighted chi-square on identical rows.
- No post-hoc band edits allowed for any already-run mission subset.

## Scaling Form (Locked)

```text
|a_res| = A0 * (|v|/v0)^p * (r_p/r0)^(-q) * (|grad(Sigma)|/g0)^s * f_io
```

- `v0`, `r0`, `g0` are fixed reference scales from DS-005 preprocessing.
- `f_io` is an inbound/outbound geometry selector (fixed sign convention).

## Locked Numeric Band (v1)

- Perigee-window band: `1e-10 <= |a_res| <= 1e-8` m/s^2.
- Day-equivalent support band (diagnostic): `1e-10 <= |a_res_day| <= 1e-8` m/s^2.

## Current Audit Snapshot

- Source run: `05_validation/evidence/artifacts/qng-t-041/fit-summary.csv` (`2026-02-21`, seed `20260222`)
- Observed `amp_median`: `2.271812e-06` m/s^2 -> outside locked v1 band.
- Observed `amp_median_day_equiv`: `2.083333e-08` m/s^2 -> outside locked v1 support band.
- Audit verdict for `C-086b`: `fail` (falsified under v1 lock).

## Falsification Record (Do Not Reopen)

- `C-086b v1` is retained as permanent falsification history.
- The v1 band must not be retuned and re-labeled as confirmed.
- Any further numeric amplitude work is tracked under `C-086b2` calibration/holdout tracks.

## Promotion Gate

- `C-086a` (directional) and `C-086b` (numeric) must remain decoupled.
- `C-086b` cannot move to pass under v1 (closed/falsified).
