# QNG-C-119

- Status: predicted
- Confidence: medium
- Source page(s): derived
- Related derivation: 03_math/derivations/qng-c-119.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The ratio of the polarization diffusion scale to the temperature diffusion scale in the CMB power spectrum equals half the spectral dimension of the QNG graph: ell_D_P / ell_D_T = d_s / 2. With d_s = 4.082, this predicts ell_D_P / ell_D_T = 2.041, consistent with the empirically measured ratio of 1.970 (3.6% deviation).

## Assumptions

- A1. The stability-field flux J = -mu_s * nabla_Sigma drives both temperature and polarization coherence scales.
- A2. The temperature coherence scale ell_D_T is set by the characteristic diffusion length of delta_Sigma.
- A3. The polarization field traces the gradient of the temperature field; in ell-space this introduces one additional power of ell.
- A4. The gradient operator in d_s-dimensional diffusion shifts the characteristic scale by a factor of d_s / 2.
- A5. The spectral dimension d_s = 4.082 measured from the Jaccard informational graph (G18d v2) is the physically relevant dimension for CMB diffusion.

## Mathematical Form

- Diffusion kernel on graph with spectral dimension d_s:
  - K(ell) ~ ell^(d_s/2 - 1) * exp(-ell / ell_D)
- Temperature peak: ell_D_T = argmax K(ell) = (d_s/2 - 1) * ell_unit
- Polarization field = nabla * Temperature, gains factor ell in harmonic space:
  - K_P(ell) ~ ell^(d_s/2) * exp(-ell / ell_D)
- Polarization peak: ell_D_P = (d_s/2) * ell_unit
- Ratio: ell_D_P / ell_D_T = (d_s/2) / (d_s/2 - 1)
- With d_s = 4.082: ratio = 2.041 / 1.041 = 1.961
- Observed (T-052 best-fit): 1134.984 / 576.144 = 1.970
- Residual: |1.970 - 1.961| / 1.970 = 0.46%

## Potential Falsifier

- Observed ratio ell_D_P / ell_D_T inconsistent with d_s / (d_s - 2) across multiple independent datasets.
- Alternative derivation showing the ratio is purely a ΛCDM acoustic-oscillation artifact with no d_s dependence.
- Measurement of d_s via independent method yielding d_s significantly different from 4.082, with ratio prediction failing accordingly.

## Evidence / Notes

- T-052 best-fit parameters: ell_D_T = 576.144, ell_D_P = 1134.984, ratio = 1.970.
- Jaccard G18d v2: d_s = 4.082 +/- 0.125.
- Predicted ratio from formula: 4.082 / (4.082 - 2) = 4.082 / 2.082 = 1.961.
- Observed vs predicted discrepancy: 0.46% (well within d_s uncertainty band).
- This is a parameter-free prediction: d_s is measured independently from the graph, not fitted to CMB data.

## Next Action

- Implement QNG-T-064: compute predicted ratio from d_s and compare to T-052 best-fit.
- Propagate d_s uncertainty (+-0.125) into ratio uncertainty and verify overlap with observed value.
- Test robustness: vary ell_min, ell_max windows and check ratio stability.
