# QNG-C-086

- Status: predicted
- Confidence: medium
- Source page(s): page-063
- Related derivation: 03_math/derivations/qng-c-086.md
- Register source: 02_claims/claims-register.md

## Claim Statement

`QNG-C-086` is treated as a split claim with two linked parts:
- `C-086a` (robust signature): near perigee, residual acceleration must be directional and aligned with `v . grad(Sigma)`.
- `C-086b v1` (numeric band v1): falsified under locked preregistration and retained as permanent fail history.
- `C-086b2` (calibration branch): near-perigee amplitude follows a recalibrated pre-registered scaling band and is pending out-of-sample confirmation.
- `C-086b3` (scaling-law branch): covariate-dependent amplitude model with disjoint append-only holdout policy.

## Assumptions

- A1. Lag acceleration is first-order in the directional derivative of the stability field.
- A2. Near-perigee segments maximize observability because both `|v|` and field-gradient variation are high.
- A3. Non-gravitational corrections (thermal recoil, SRP, drag, maneuvers) are carried explicitly before fitting.
- A4. A single `tau` family (or explicitly stated `tau(chi)` law) should remain non-chaotic across comparable trajectory slices.
- A5. Amplitude is not constant; it scales with geometry and field context.

## Mathematical Form

- Core lag operator:
- `a_res = -tau * (v . grad) grad(Sigma)`
- Split form:
- `C-086a`: `sign(a_res_parallel) = sign(v . grad(Sigma))` near perigee, with directional-score and sign-consistency gates.
- `C-086b2`: `|a_res| = A0 * (|v|/v0)^p * (r_p/r0)^(-q) * (|grad(Sigma)|/g0)^s * f_io`
- `C-086b3`: `log(A_obs+eps) = b0 + b1*log(v_p/v0) + b2*log((h_p+h0)/h0) + b3*log(|grad_g|/g0) + b4*log(1+geom_io) + b5*log(1+non_grav/ng0) + e`
- where `f_io` encodes inbound/outbound geometry and orientation term.
- Pre-registered band is evaluated against day-equivalent and perigee-window amplitudes (same row set, same sigma, same likelihood).

## Potential Falsifier

- `C-086a` falsified if directional alignment/sign consistency disappears after controls and robustness checks.
- `C-086b v1` is already falsified by locked strict audit.
- `C-086b2` falsified if locked holdout runs fail strict gates without any threshold edits.
- `C-086b3` falsified if disjoint locked holdout fails after b3 prereg is fixed; blocked state is used only for missing data rows.
- Cross-domain falsifier: no consistent sign structure between flyby and deep-space anchor subsets under shared gating.

## Evidence / Notes

- `C-086a` is supported by `QNG-T-041` real cross-domain run (`2026-02-21`) with directional and robustness gates passing.
- `C-086b v1` is permanently fail under:
- `05_validation/pre-registrations/qng-c-086b-amplitude-band-v1.md`
- `C-086b2` calibration lock is tracked in:
- `05_validation/pre-registrations/qng-c-086b-amplitude-band-v2.md`
- `C-086b2` out-of-sample lock is tracked in:
- `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`
- `C-086b3` scaling lock is tracked in:
- `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md`
- Holdout append-only ledger:
- `05_validation/pre-registrations/holdout-registry.csv`

## Next Action

- Keep `C-086a` and amplitude tracks separated in decisions (robust signature vs numeric amplitude).
- Keep `C-086b v1` as frozen falsification history.
- Keep `C-086b2` labeled calibration/pending until strict holdout passes on new non-control mission slices.
- Keep `C-086b3` on blocked/pending until disjoint holdout IDs are ingested and evaluated without gate changes.
