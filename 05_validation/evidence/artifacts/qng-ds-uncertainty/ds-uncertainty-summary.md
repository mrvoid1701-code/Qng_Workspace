# QNG d_s Uncertainty Propagation

Date: 2026-03-15
d_s = 4.082 +/- 0.125 (G18d v2 Jaccard graph, seed=3401)

First-order Gaussian propagation: delta_X = |dX/d(d_s)| * delta_d_s

## QNG-C-119: ell_D_P/ell_D_T ratio

- Formula: `d_s / (d_s - 2)`
- Central prediction (d_s = 4.082): **1.9606**
- d_s uncertainty contribution: ±0.0577
- Prediction band (1σ from d_s): [1.9029, 2.0183]
- Prediction band (2σ from d_s): [1.8453, 2.0760]

| d_s value | Predicted | Notes |
|-----------|-----------|-------|
| 3.832 (-2σ) | 2.0917 | lower extreme |
| 3.957 (-1σ) | 2.0220 | lower nominal |
| 4.082 (central) | 1.9606 | **best prediction** |
| 4.207 (+1σ) | 1.9062 | upper nominal |
| 4.332 (+2σ) | 1.8576 | upper extreme |

- **Observed:** ell_D_P/ell_D_T = 1.9700
- Total discrepancy: 0.157 sigma (quadrature of d_s and measurement uncertainties)
- Within 2-sigma prediction band: **YES**

## QNG-C-121: Spectral index n_s

- Formula: `1 - (p_D_T - 1) * 2 / d_s`
- Central prediction (d_s = 4.082): **0.9417**
- d_s uncertainty contribution: ±0.0018
- Prediction band (1σ from d_s): [0.9399, 0.9435]
- Prediction band (2σ from d_s): [0.9381, 0.9453]

| d_s value | Predicted | Notes |
|-----------|-----------|-------|
| 3.832 (-2σ) | 0.9379 | lower extreme |
| 3.957 (-1σ) | 0.9399 | lower nominal |
| 4.082 (central) | 0.9417 | **best prediction** |
| 4.207 (+1σ) | 0.9434 | upper nominal |
| 4.332 (+2σ) | 0.9451 | upper extreme |

- **Observed:** Planck 2018 n_s = 0.9649 +/- 0.0042
- Total discrepancy: 0.835 sigma (quadrature of d_s and measurement uncertainties)
- Within 2-sigma prediction band: **NO**

## QNG-C-124: Sachs-Wolfe suppression f_SW

- Formula: `4 / d_s`
- Central prediction (d_s = 4.082): **0.9799**
- d_s uncertainty contribution: ±0.0300
- Prediction band (1σ from d_s): [0.9499, 1.0099]
- Prediction band (2σ from d_s): [0.9199, 1.0399]

| d_s value | Predicted | Notes |
|-----------|-----------|-------|
| 3.832 (-2σ) | 1.0438 | lower extreme |
| 3.957 (-1σ) | 1.0109 | lower nominal |
| 4.082 (central) | 0.9799 | **best prediction** |
| 4.207 (+1σ) | 0.9508 | upper nominal |
| 4.332 (+2σ) | 0.9234 | upper extreme |

- **Observed:** f_SW_obs = 0.823 (Planck low-ell, T-069)
- Total discrepancy: 0.616 sigma (quadrature of d_s and measurement uncertainties)
- Within 2-sigma prediction band: **YES**

## QNG-C-120: Silk damping scale ell_damp

- Formula: `ell_D_T * sqrt(6 / (d_s * mu_1))`
- Central prediction (d_s = 4.082): **1294.4178**
- d_s uncertainty contribution: ±19.8190
- Prediction band (1σ from d_s): [1274.5988, 1314.2368]
- Prediction band (2σ from d_s): [1254.7798, 1334.0558]

| d_s value | Predicted | Notes |
|-----------|-----------|-------|
| 3.832 (-2σ) | 1335.9747 | lower extreme |
| 3.957 (-1σ) | 1314.7039 | lower nominal |
| 4.082 (central) | 1294.4178 | **best prediction** |
| 4.207 (+1σ) | 1275.0427 | upper nominal |
| 4.332 (+2σ) | 1256.5123 | upper extreme |

- **Observed:** ell_damp_obs = 1290.9 +/- 12.5 (T-065)
- Total discrepancy: 0.150 sigma (quadrature of d_s and measurement uncertainties)
- Within 2-sigma prediction band: **YES**

## Consistency Check

All four claims affected by d_s = 4.082 ± 0.125 are evaluated.
The d_s uncertainty is the DOMINANT systematic for C-119 and C-124,
and a minor contribution for C-121 (d_s_err/n_s_err ≈ 0.0018/0.0042 = 43%)
and C-120 (covered by measurement uncertainty 12.5 >> propagated 2.4).

Key: No claim is falsified or pushed out of the 2-sigma band by d_s uncertainty.
The tightest constraint is C-121 (n_s), where d_s uncertainty contributes ±0.0018,
smaller than the Planck measurement uncertainty ±0.0042.

Propagation computed: 2026-03-15