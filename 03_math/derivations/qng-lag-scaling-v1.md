# QNG Lag Scaling at Large Distance (v1)

Date: 2026-02-25  
Scope: Qualitative distance scaling of the lag-induced acceleration in QNG, independent of the absolute value of τ.

## Setup
- Weak-field, single central mass M (Sun) with potential Σ(r) ≈ −GM/r.
- Metric close to flat: g^{ij} ≈ δ^{ij}.
- Lag term (directional): \(a_{\text{lag}} = -\,\tau\, (v\cdot\nabla)\,(g^{-1}\nabla \Sigma)\).
- Assume probe velocity is approximately radial and slowly varying with r (|v| ≈ const over the interval of interest).

## Scaling
For Σ = −GM/r and g^{-1} ≈ I:
- Gradient: \(\nabla \Sigma = +GM\, r^{-2}\, \hat{r}\).
- Apply directional derivative along v ≈ v_r \hat{r}:
\[
(v\cdot\nabla)(\nabla \Sigma) \;\sim\; v_r\, \frac{d}{dr}\left(GM\, r^{-2}\right)\hat{r}
         = v_r\, (-2 GM)\, r^{-3}\, \hat{r}.
\]
- Therefore
\[
|a_{\text{lag}}| \;\propto\; \tau\, v_r\, \frac{GM}{r^{3}}.
\]

Compare with Newtonian magnitude:
\[
|a_{\text{N}}| = \frac{GM}{r^{2}}.
\]

Ratio:
\[
\frac{|a_{\text{lag}}|}{|a_{\text{N}}|} \;\propto\; \tau\, v_r\, \frac{1}{r}.
\]

Key qualitative consequence (independent of τ units):
- The lag contribution decays as 1/r³ in absolute value, i.e. one power of r faster than Newton (1/r²).
- Relative to Newton, the lag/N ratio decays as 1/r. At large r, the lag term becomes progressively **smaller** than Newton unless τ or v_r grow with r.

## When can it look “almost constant”?
- If the probe is on (nearly) constant-acceleration coast with slowly decreasing v_r and the observation window is narrow in r, a 1/r variation may appear quasi-constant over that window.
- Over decades in r (e.g., 20–70 AU), the 1/r factor is a clear slope: \(|a_{\text{lag}}|\) would drop by ~3.5× from 20→70 AU for fixed τ,v_r.

## Implication
- A τ calibrated on inner flybys cannot by itself yield a flat anomaly at outer distances; the functional form of the lag term predicts a faster falloff (1/r³ absolute, 1/r relative). Achieving a distance-independent anomaly would require an additional scaling of τ or of the kernel with r or |∇Σ|, or a different lag operator.

## Independence from τ normalization
This argument uses only dimensional scaling of the operator; it does not depend on the numerical value or units of τ. Until the graph-to-physical scaling is specified, no absolute prediction is possible, but the **shape** (faster decay than Newton) is fixed by the operator form above.***
