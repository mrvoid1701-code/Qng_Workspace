# QNG-C-126

- Status: tested
- Confidence: medium
- Source page(s): derived
- Related derivation: G29 gate (scripts/run_qng_g29_gn_scaling_v1.py)
- Register source: 02_claims/claims-register.md

## Claim Statement

The effective Newton constant G_N_eff, defined as the amplitude A(k) of the dipole
Green's function G_dipol(r;k) ≈ A(k)·r^{slope(k)}, decreases with graph connectivity k.
Specifically: (a) A(k) is a power-law in k with slope ∈ (−3.0, −0.5), consistent with
G_N_eff ∝ k^{−2.2} ≈ 1/k², (b) the spectral gap μ₁(k) is strictly monotone increasing
with k (Weyl theorem), (c) μ₁(k) is a power-law in k with slope ≈ 1.79 — consistent
with the Wigner formula k−2√k at finite k∈[4,12], and (d) the amplitude A(k) scales
as μ₁(k)^{−β} with β ≈ 1.25, in the range (0.5, 2.0) predicted by the spectral
decomposition of the graph Green's function.

## Gate results (2026-03-21, seed=3401, N=280, k_scan=[4,6,8,10,12])

| Gate | Result | Value | Threshold |
|------|--------|-------|-----------|
| G29a | PASS | slope_A = −2.233 (r²=0.999) | (−3.0, −0.5) |
| G29b | PASS | μ₁ monotone: [0.678, 1.678, 2.689, 3.800, 4.928] | strict ↑ |
| G29c | PASS | slope_μ₁ = 1.794 (r²=0.990) | (0.5, 2.5) |
| G29d | PASS | β = slope_A/slope_μ₁ = −1.245 | (−2.0, −0.5) |
| **ALL** | **PASS** | 4/4 | — |

Cross-seed robustness (all 4/4 PASS):
- seed=1111: slope_A=−2.250, slope_μ₁=1.693, β=−1.329
- seed=2222: slope_A=−2.316, slope_μ₁=1.741, β=−1.330
- seed=4999: slope_A=−2.181, slope_μ₁=1.880, β=−1.160

## Assumptions

- A1. The QNG graph substrate (Jaccard, N=280, k_init=8) is the canonical graph from G17v2/G18d.
- A2. k_conn ∈ {4,6,8,10,12} are the scan values; k_init=8 is fixed (same Jaccard similarity structure).
- A3. G_N_eff ≡ A(k) = exp(OLS intercept of log-log fit of dipole shell amplitudes).
- A4. μ₁(k) is computed by inverse power iteration with zero-mode deflation, reg=1e-6.
- A5. Thresholds are derived from Wigner formula k−2√k at finite k∈[4,12] + spectral decomposition.

## Mathematical Form

G_N_eff(k) ≡ A(k) where G_dipol(r;k) = A(k) · r^{slope(k)}.

From spectral decomposition:
  G(i,j) = Σ_α φ_α(i)φ_α(j)/(λ_α + m²)  →  A(k) ∝ μ₁(k)^{−β}  with β ≈ 1.

From Wigner (finite k):
  μ₁(k) ≈ k − 2√k  →  OLS slope in log-log ≈ 2.0–2.2 for k∈[4,12].

Therefore: A(k) ∝ k^{−slope_μ₁ × β} ≈ k^{−2.2} (measured: k^{−2.23}).

Measured exponents (seed=3401):
  μ₁ = [0.678, 1.678, 2.689, 3.800, 4.928] for k = [4, 6, 8, 10, 12]
  A   = [0.089, 0.036, 0.020, 0.011, 0.008] for k = [4, 6, 8, 10, 12]

## Physical Interpretation

G29 demonstrates that the effective gravitational coupling G_N_eff is inversely
related to graph connectivity: denser graphs (larger k) are "spectrally stiffer"
(larger μ₁) and thus have smaller long-range propagator amplitudes.

The scaling G_N_eff ∝ k^{−α} with α ≈ 2.2 provides the first quantitative connection
between QNG graph topology (k) and the effective Newton constant. The leading-order
spectral prediction G_N_eff ∝ 1/μ₁(k) is confirmed by G29d (β ≈ 1.25 close to 1).

The canonical QNG graph (k=8) sits at the center of the (3.5 < d_s < 4.5) window
(from the phase diagram sweep, NEXT_STEPS.md), and G_N_eff(k=8) provides the
reference normalization for all G_N-related predictions.

## Limitations

- k_init=8 is fixed while k_conn varies: this tests connectivity scaling within the
  same Jaccard similarity structure, not independent Jaccard constructions at each k.
- The exponent α ≈ 2.2 includes finite-size corrections; asymptotic theory predicts α → 1.
- d_s(k) varies across k (from ~3.5 at k=6 to ~4.5 at k=10), which partly contaminates
  the amplitude measurement. A clean G_N scaling requires d_s fixed (future: fix d_s
  by varying N and k together along the d_s=4 ridge).
- Absolute normalization of G_N_eff is not yet connected to the continuum G_N value;
  only the scaling behavior is tested here.
