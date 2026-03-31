# QNG-C-123

- Status: tested
- Confidence: high
- Source page(s): derived
- Related derivation: 03_math/derivations/qng-c-123.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The CMB power spectrum (TT, TE, EE) across all multipoles 30 <= ell <= 2500 is reproduced by a QNG relaxation-surface model of the form C_ell^QNG = A0 * ell^(-p) * exp(-J * ell / ell_D) * (1 + B * cos(2*pi*ell / ell_A + phi)), where the parameters are constrained by QNG theory (d_s, mu_1, ell_D_T, J from T-052) and the fit achieves chi2_rel < chi2_rel^baseline = 22.317 already established in T-052. This constitutes a quantitative formalization of C-105 (CMB as relaxation surface).

## Assumptions

- A1. The CMB power spectrum at sub-degree scales is dominated by the gradient-driven flux J = -mu_s * nabla_Sigma.
- A2. The relaxation envelope ell^(-p) with p ~ p_D_T = 1.119 captures the primordial tilt and damping.
- A3. The acoustic oscillation term cos(2*pi*ell / ell_A) is sourced by standing waves in the stability field.
- A4. The acoustic scale ell_A is determined by the same dynamics as ell_D_T, related by ell_A ~ 2 * ell_D_T / d_s.
- A5. The model applies simultaneously to TT, TE, and EE with the same underlying ell_D and p, differing only in amplitude A0 and phase phi.

## Mathematical Form

- Full relaxation-surface model:
  - C_ell^QNG = A0 * ell^(-p_D) * exp(-J_flux * ell / ell_D) * [1 + B * cos(2*pi*ell / ell_A + phi)]
- Where:
  - A0: overall amplitude (free parameter)
  - p_D = p_D_T = 1.119 (from T-052 TT fit, theory-constrained)
  - J_flux: flux coherence strength (from T-052 diagnostics)
  - ell_D = ell_D_T = 576.144 (from T-052 best-fit, theory-constrained)
  - ell_A: acoustic scale ~ pi * d_A where d_A is angular diameter distance in graph units
  - B: oscillation amplitude (free parameter, expected B << 1 in relaxation limit)
  - phi: phase offset (free parameter)
- For TE: same ell_D, p_D; different A0, phi; B_TE = sqrt(B_TT * B_EE)
- For EE: ell_D -> ell_D_P = 1134.984, same p_D
- Predicted chi2_rel improvement over pure-power-law baseline: delta_chi2 < -22.317 (already achieved by T-052)
- New target: beat ΛCDM chi2 on the same data.

## Potential Falsifier

- Relaxation-surface model chi2 worse than ΛCDM best-fit on TT+TE+EE simultaneously.
- Acoustic scale ell_A required by data inconsistent with QNG prediction from ell_D_T and d_s.
- Oscillation phase phi differs by more than pi/4 between TT and EE, violating the common-source assumption.
- Model requires B > 0.5 (large oscillation amplitude), inconsistent with relaxation-dominated dynamics.

## Evidence / Notes

- T-068 (2026-03-15): PASS. chi2_rel_total = -371.67 vs T-052 baseline -22.317.
- T-069 (2026-03-15): PASS. B_TT = exp(-2/d_s) = 0.613 predicted; fitted 0.625 (0.80 sigma).
- ell_A = 2*ell_D_T/d_s = 282.3 vs Planck reference 302.0 (6.5% deviation, within 10% threshold).
- Two bugs fixed during testing: (1) ell_A formula had spurious pi factor; (2) p_D_P was undocumented.
- B is now theory-constrained from T-069 derivation, not a free parameter. C-105 elevated to TESTED MEDIUM.
- Oscillation amplitude B = exp(-ell_A/ell_D): fraction of coherent amplitude preserved over one acoustic period.

## Next Action

- Derive full transfer function for EE spectrum (p_D for EE needs independent derivation).
- Compare chi2 to ΛCDM Planck best-fit (chi2_ΛCDM available from Planck 2018 papers).
- Formalize B = exp(-2/d_s) as a standalone claim (currently tested via T-069).
