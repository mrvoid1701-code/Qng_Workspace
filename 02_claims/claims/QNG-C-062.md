# QNG-C-062

- Status: predicted
- Confidence: low
- Source page(s): page-040,page-084
- Related derivation: 03_math/derivations/qng-c-062.md
- Register source: 02_claims/claims-register.md

## Claim Statement

N-body simulations incorporating stability-field memory kernels should reproduce large-scale structure and dynamical signatures consistent with QNG predictions, without requiring particle dark matter components.

## Assumptions

- A1. Gravitational behavior is governed by the stability field Σ\SigmaΣ with memory dynamics.
- A2. Memory kernels capture delayed responses to evolving mass–Straton distributions.
- A3. Structure formation emerges from stability-driven interactions among nodes or particles.
- A4. Numerical simulations can approximate the coarse-grained behavior of the underlying network.
- A5. Observable cosmological structures reflect aggregated stability-field evolution.

## Mathematical Form

- Memory-based stability field:
- Σ(x,t)=∫−∞tK(t−t′) χ(x,t′) dt′\Sigma(x,t) = \int_{-\infty}^{t} K(t - t') \, \chi(x,t') \, dt'Σ(x,t)=∫−∞tK(t−t′)χ(x,t′)dt′
- Effective gravitational acceleration:
- a⃗=−∇Σ\vec{a} = - \nabla \Sigmaa=−∇Σ
- Particle evolution equation:
- d2x⃗idt2=−∇Σ(x⃗i,t)\frac{d^2 \vec{x}_i}{dt^2} = - \nabla \Sigma(\vec{x}_i, t)dt2d2xi=−∇Σ(xi,t)
- Kernel example:
- K(τ)=1τ0e−τ/τ0K(\tau) = \frac{1}{\tau_0} e^{-\tau/\tau_0}K(τ)=τ01e−τ/τ0
- Structure comparison metric:
- SQNG≈SobservedS_{\text{QNG}} \approx S_{\text{observed}}SQNG≈Sobserved

## Potential Falsifier

- Simulations with memory kernels failing to reproduce observed large-scale structures.
- Observations requiring particle dark matter even when memory dynamics are included.
- Demonstration that stability-based gravity cannot generate realistic cosmological evolution.
- Empirical necessity for alternative mechanisms inconsistent with QNG predictions.

## Evidence / Notes

- T-029 (2026-03-15): PASS — causal exponential kernel (tau=1.3, k=0.85) reduces chi2
  by 671 units (12 seeds, delta_chi2 = -671.49 vs baseline). Memory kernel improves
  cluster-position agreement with truth trajectory by ~100-3400x over instantaneous model.
- T-029-NC (2026-03-15): Partial negative controls. 4 NCs tested; 2/4 pass:
  - NC-1 (tau=0, no memory): PASS — mean ratio 1334x. Memory is essential.
  - NC-4 (wrong sign): PASS — mean ratio 1365x. Causal sign is essential.
  - NC-2 (tau=0.2, too short): FAIL — chi2 observable inconsistent (2 seeds fail gate).
  - NC-3 (tau=8.0, too long): FAIL — longer tau also reaches similar equilibrium positions.
  Methodological finding: the equilibrium chi2 metric is insensitive to tau specificity.
  NC-2/NC-3 failures reveal that cluster equilibrium positions do not discriminate tau
  within a factor ~6x. A trajectory-based chi2 (all timesteps, not just final) is needed
  to constrain tau. This is a documented limitation of the current observable.
- Evidence level: Bronze-plus — positive result confirmed, memory and correct sign are
  both necessary (NC-1, NC-4 strong at 1000-1400x ratio). Tau specificity not yet
  demonstrated with the equilibrium observable.

## Next Action

- Implement trajectory-based chi2 (compare full simulation history, not just equilibrium)
  to discriminate tau values in NC-2/NC-3 controls.
- Run T-029-NC v2 with trajectory-chi2 observable: expect NC-2 (tau=0.2) and NC-3
  (tau=8.0) to fail to replicate the tau=1.3 trajectory shape.
- Extend to 3D spatial simulation with cosmological initial conditions for cosmological
  structure comparison (current test is 2D, small-scale cluster dynamics).
