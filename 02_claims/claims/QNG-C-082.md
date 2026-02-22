# QNG-C-082

- Status: predicted
- Confidence: medium
- Source page(s): page-060,page-064
- Related derivation: 03_math/derivations/qng-c-082.md
- Register source: 02_claims/claims-register.md

## Claim Statement

The excess velocity observed in galactic rotation curves can be explained by the contribution of historical stability-field memory, where lagged Σ\SigmaΣ from prior mass distributions produces additional effective gravitational acceleration beyond the instantaneous baryonic contribution.

## Assumptions

- A1. The stability field Σ\SigmaΣ retains historical information through memory kernels.
- A2. Galactic mass distributions evolve over time, generating lagged stability contributions.
- A3. Effective gravitational acceleration depends on both instantaneous and historical components.
- A4. Rotation-curve measurements reflect the current state of the stability field.
- A5. Particle dark matter is not required if memory contributions are sufficient.

## Mathematical Form

- Memory-based stability field:
- Σ(x,t)=∫−∞tK(t−t′) χ(x,t′) dt′\Sigma(x,t) = \int_{-\infty}^{t} K(t - t') \, \chi(x,t') \, dt'Σ(x,t)=∫−∞tK(t−t′)χ(x,t′)dt′
- Lag contribution:
- ΔΣ=Σhistorical−Σinstantaneous\Delta \Sigma = \Sigma_{\text{historical}} - \Sigma_{\text{instantaneous}}ΔΣ=Σhistorical−Σinstantaneous
- Effective gravitational acceleration:
- g⃗eff=−∇Σ=−∇(Σinst+ΔΣ)\vec{g}_{\text{eff}} = - \nabla \Sigma = - \nabla (\Sigma_{\text{inst}} + \Delta \Sigma)geff=−∇Σ=−∇(Σinst+ΔΣ)
- Circular velocity relation:
- v2(r)=r ∣g⃗eff∣v^2(r) = r \, |\vec{g}_{\text{eff}}|v2(r)=r∣geff∣
- Excess velocity condition:
- vobserved>vbaryonic⇒ΔΣ≠0v_{\text{observed}} > v_{\text{baryonic}} \quad \Rightarrow \quad \Delta \Sigma \neq 0vobserved>vbaryonic⇒ΔΣ=0

## Potential Falsifier

- Observations showing rotation curves incompatible with any memory-based contribution.
- Direct detection of particle dark matter explaining rotation curves independently.
- Demonstration that historical mass distributions cannot produce observed effects.
- Empirical necessity for additional unseen mass components.

## Evidence / Notes

- Provides an alternative explanation for galactic rotation anomalies.
- Conceptually consistent with delayed-response gravitational models.
- Connects dark-matter–like behavior to dynamical history of galaxies.
- Empirical validation depends on quantitative agreement with rotation-curve data.

## Next Action

- Derive quantitative rotation-curve predictions for realistic galaxy models.
- Compare predictions with observational datasets.
- Constrain kernel parameters using galactic data.
- Develop simulations illustrating memory-induced rotation behavior.
