# QNG-C-120

- Status: predicted
- Confidence: medium
- Source page(s): derived
- Related derivation: 03_math/derivations/qng-c-120.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The CMB damping tail (Silk damping) at high multipoles ell > 1000 follows an exponential cutoff whose characteristic scale ell_damp is determined by the spectral gap mu_1 and the spectral dimension d_s of the QNG graph: ell_damp = pi * (d_s / 4)^(1/2) / sqrt(mu_1). With mu_1 = 0.291 and d_s = 4.082, this predicts ell_damp ~ 10.2 in graph units, convertible to multipole space via the ell_D_T calibration anchor.

## Assumptions

- A1. High-ell power suppression corresponds to diffusion on the QNG graph beyond the coherence length.
- A2. The spectral gap mu_1 controls the exponential decay rate of the diffusion kernel at large separations.
- A3. The spectral dimension d_s modulates the effective diffusion volume available at each scale.
- A4. The damping envelope in multipole space takes the form: D(ell) = exp(-ell^2 / ell_damp^2).
- A5. The ell_D_T = 576 best-fit anchor converts graph-unit diffusion lengths to observed multipoles.

## Mathematical Form

- Lazy random walk propagator on graph at time t:
  - P(t) ~ sum_k exp(-lambda_k * t) where lambda_k are Laplacian eigenvalues
- Spectral gap mu_1 = min non-zero eigenvalue = 0.291
- Diffusion length at time t: L(t) ~ t^(1/d_s) * mu_1^(-1/2)
- Damping wavenumber: k_damp = 1 / L ~ mu_1^(1/2) * t^(-1/d_s)
- In ell-space (t = recombination epoch, mapped via ell_D_T):
  - ell_damp = pi * sqrt(d_s / 4) / sqrt(mu_1)
  - ell_damp = pi * sqrt(4.082 / 4) / sqrt(0.291)
  - ell_damp = pi * 1.010 / 0.539 = 5.89 (graph units)
- Conversion to multipole: ell_damp^obs = ell_damp * ell_D_T / ell_unit
- Damping profile: C_ell^damp = C_ell^base * exp(-(ell / ell_damp^obs)^2)

## Potential Falsifier

- Observed high-ell power spectrum inconsistent with exponential damping of this form.
- Damping scale measured from data incompatible with mu_1 and d_s within their uncertainty ranges.
- Demonstration that the damping is fully explained by photon diffusion (Silk) without any graph-spectral contribution.

## Evidence / Notes

- mu_1 = 0.291 measured from G17 (Jaccard graph, n=280, k=8, seed=3401).
- d_s = 4.082 +/- 0.125 from G18d v2.
- Planck TT data extends to ell = 2500; damping is clearly visible above ell ~ 1500.
- The predicted ell_damp in graph units must be calibrated against the ell_D_T anchor to yield observable predictions.
- This test connects two independently measured QNG quantities (mu_1, d_s) to a third observable (damping scale).

## Next Action

- Implement QNG-T-065: extract empirical damping scale from TT spectrum (ell > 1000) via exponential fit.
- Compute predicted ell_damp from mu_1 and d_s, convert to multipole using ell_D_T anchor.
- Compare predicted vs observed ell_damp with propagated uncertainties.
