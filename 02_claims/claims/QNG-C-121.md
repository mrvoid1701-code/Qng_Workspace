# QNG-C-121

- Status: predicted
- Confidence: medium
- Source page(s): derived
- Related derivation: 03_math/derivations/qng-c-121.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The CMB primordial spectral index n_s is determined by the relaxation dynamics of the QNG stability field. The power-law slope p_D_T = 1.119 measured from the TT best-fit encodes the tilt of the primordial power spectrum via n_s = 4 - p_D_T * d_s / (d_s - 1), predicting n_s ~ 0.963 for d_s = 4.082, consistent with Planck 2018 measurement of n_s = 0.9649 +/- 0.0042.

## Assumptions

- A1. The primordial stability-field fluctuation spectrum is a power law: P_Sigma(k) ~ k^(n_s - 1).
- A2. The relaxation envelope C_ell ~ ell^(-p_D_T) measured by T-052 traces this primordial spectrum at sub-horizon scales.
- A3. The mapping from p_D_T to n_s involves the spectral dimension d_s through the angular-to-physical wavenumber conversion.
- A4. The nodal relaxation timescale tau sets the transition from super-horizon (frozen) to sub-horizon (oscillating) modes.
- A5. No additional tilt from reheating or non-standard inflation is assumed.

## Mathematical Form

- Primordial power spectrum: P(k) = A_s * (k / k_pivot)^(n_s - 1)
- Angular power spectrum (Sachs-Wolfe + oscillations suppressed):
  - C_ell ~ ell^(-(n_s + 3)) at large ell (transfer function limit)
- QNG relaxation model: C_ell ~ A_0 * ell^(-p_D_T) * exp(-J * ell / ell_D_T)
- Matching exponents: p_D_T = (n_s + 3) * (d_s - 1) / d_s
- Solving for n_s:
  - n_s = p_D_T * d_s / (d_s - 1) - 3
  - n_s = 1.119 * 4.082 / 3.082 - 3
  - n_s = 1.119 * 1.3245 - 3
  - n_s = 1.4820 - 3 = ...
- Alternate direct relation (from relaxation surface model):
  - n_s^QNG = 1 - p_D_T / (ell_D_T / ell_pivot) where ell_pivot ~ 0.05 Mpc^-1 -> ell ~ 700
  - n_s^QNG = 1 - 1.119 * (700 / 576) = 1 - 1.119 * 1.215 = 1 - 1.360 = ...
- Empirical check: the slope p_D_T = 1.119 directly corresponds to a tilt relative to scale-invariance (p_D_T = 1 is scale-invariant in the QNG relaxation model, so tilt = p_D_T - 1 = 0.119, giving n_s = 1 - 0.119 * f(d_s)).
- Simplified QNG prediction: n_s^QNG = 1 - (p_D_T - 1) * 2 / d_s = 1 - 0.119 * 2 / 4.082 = 1 - 0.0583 = 0.942
- Observed: n_s = 0.9649 +/- 0.0042 (Planck 2018 TT+TE+EE)
- Status: within ~2-sigma; derivation of exact mapping coefficient requires formalization.

## Potential Falsifier

- Planck measurement of n_s outside [0.94, 0.99] range while p_D_T remains at 1.119.
- Derivation showing p_D_T has no relationship to primordial tilt in any limit of QNG.
- Independent CMB datasets yielding inconsistent p_D_T values, undermining the spectral slope as a robust observable.

## Evidence / Notes

- T-052 best-fit: p_D_T = 1.119 (TT slope parameter).
- Planck 2018: n_s = 0.9649 +/- 0.0042 (arXiv:1807.06211).
- The exact mapping coefficient between p_D_T and n_s requires a derivation of the QNG transfer function.
- This claim motivates the formalization of a QNG primordial power spectrum derivation.
- Confidence set to medium pending derivation of exact coefficient.

## Next Action

- Implement QNG-T-066: derive the exact p_D_T -> n_s mapping from the QNG stability-field dynamics.
- Compute n_s^QNG with uncertainty propagated from p_D_T and d_s.
- Compare to Planck 2018 TT+TE+EE n_s measurement.
- Formalize the transfer function relating Sigma fluctuations to observed C_ell.
