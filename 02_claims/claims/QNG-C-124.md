# QNG-C-124

- Status: predicted
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
- Confidence set to LOW due to cosmic variance dominance making a clean test statistically challenging.
- This test is most useful as a qualitative consistency check, not a precision falsifier.

## Next Action

- Implement QNG-T-069: compute mean Delta_SW from Planck TT in [2, 30] and compare to QNG prediction.
- Propagate d_s uncertainty into f_SW uncertainty band.
- Assess whether QNG suppression is distinguishable from cosmic variance and known low-ell anomaly.
- Compare directional prediction (deficit, not excess) to observed Planck low-ell behavior.
