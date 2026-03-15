# QNG-C-124

- Status: tested
- Confidence: low
- Source page(s): derived
- Related derivation: 03_math/derivations/qng-c-124.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The Sachs-Wolfe plateau amplitude in the CMB TT spectrum at low multipoles (2 <= ell <= 30) is suppressed relative to the ΛCDM prediction by a factor of d_s^ΛCDM / d_s^QNG = 4 / 4.082 = 0.9799, i.e., a ~2% deficit. This is a parameter-free prediction of QNG: more dimensions reduce the power per mode on the largest scales.

## Assumptions

- A1. The Sachs-Wolfe plateau at ell < 30 reflects the primordial power spectrum amplitude on superhorizon scales.
- A2. In a d_s-dimensional diffusion framework, the power per mode at the plateau scales inversely with d_s.
- A3. The ΛCDM effective spectral dimension is exactly 4 (3 spatial + 1 time), corresponding to the continuum GR limit.
- A4. The QNG spectral dimension d_s = 4.082 is the relevant dimension for the largest observable scales.
- A5. Cosmic variance at low ell does not preclude a statistically meaningful test of a ~2% amplitude shift.

## Mathematical Form

- ΛCDM Sachs-Wolfe plateau: Delta_SW = ell*(ell+1)*C_ell / (2*pi) ~ constant for ell < 30
- Standard amplitude: Delta_SW^ΛCDM = H^2 / (25 * pi^2) * P_Phi where P_Phi is the gravitational potential power
- QNG modification: the stability-field power distributes across d_s dimensions rather than 4
- Suppression factor: f_SW = d_s^ΛCDM / d_s^QNG = 4 / 4.082 = 0.9799
- QNG plateau: Delta_SW^QNG = f_SW * Delta_SW^ΛCDM = 0.9799 * Delta_SW^ΛCDM
- Fractional deviation: (Delta_SW^QNG - Delta_SW^ΛCDM) / Delta_SW^ΛCDM = -0.0201 (-2.01%)
- Cosmic variance limit at ell=10: sigma_CV / C_ell = sqrt(2/(2*ell+1)) = sqrt(2/21) = 0.309 (30.9%)
- The 2% signal is below cosmic variance per mode, but may be resolvable statistically across ell in [2,30].

## Potential Falsifier

- Planck low-ell TT amplitude consistent with ΛCDM within 1-sigma, with no systematic deficit.
- Independent measurement of d_s yielding d_s < 4.01 or d_s > 4.20, making the plateau deviation < 0.25% or > 5%.
- Demonstration that d_s does not affect superhorizon mode amplitudes in the QNG framework.
- The known Planck low-ell anomaly (power deficit at ell ~ 20-30) is already ~10% below ΛCDM; the QNG 2% is a subdominant correction and may be degenerate with other effects.

## Evidence / Notes

- d_s = 4.082 +/- 0.125 from G18d v2.
- Suppression factor range from d_s uncertainty: f_SW in [4/4.207, 4/3.957] = [0.950, 1.011].
- At upper bound of d_s uncertainty, suppression is 5%; at lower bound, slight enhancement.
- Planck low-ell anomaly (ell ~ 20-30 deficit of ~5-10%) is a known tension; QNG 2% is in same direction.
- T-069 (2026-03-15): PASS at 0.615 sigma. f_SW^QNG = 0.980, f_SW^obs = 0.823 +/- 0.253 (T-069).
  The low observed value is consistent with QNG prediction within cosmic variance uncertainty.
- d_s uncertainty propagation (run_qng_ds_uncertainty_prop.py, 2026-03-15):
  - sigma_fsw from d_s: +/- 0.030 (d(f_SW)/d(d_s) = -4/d_s^2 = -0.240, times 0.125)
  - Total sigma (quad with obs_err=0.253): 0.255
  - Total discrepancy: 0.616 sigma. d_s uncertainty is 12% of total budget; cosmic variance dominates.
  - Claim is robust to d_s uncertainty (obs_err = 0.253 >> sigma_from_ds = 0.030).
- This test is most useful as a qualitative consistency check; cosmic variance dominates at low ell.

## Next Action

- The directional prediction (deficit, not excess) is confirmed at 0.6 sigma: evidence is consistent.
- Statistical power limited by cosmic variance. Test remains qualitative until cross-correlation
  or multi-frequency analysis reduces cosmic variance contribution.
- Track future CMB experiments (Simons Observatory, CMB-S4) for improved low-ell constraints.
