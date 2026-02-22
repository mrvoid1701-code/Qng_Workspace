# QNG-C-111

- Status: derived
- Confidence: low
- Source page(s): page-077
- Related derivation: 03_math/derivations/qng-c-111.md
- Register source: 02_claims/claims-register.md

## Claim Statement

In the QNG framework, the arrow of time corresponds to irreversible update ordering within the node network, while entropy scales with the number of accessible stable reconfigurations of the system, reflecting the growth of configuration space under stability-driven dynamics.

## Assumptions

- A1. Temporal evolution proceeds through ordered node updates.
- A2. Update dynamics include stochastic or irreversible components.
- A3. Stability selection determines which configurations persist.
- A4. Entropy reflects the multiplicity of stable configurations.
- A5. Macroscopic thermodynamic behavior emerges from network dynamics.

## Mathematical Form

- Update ordering:
- t0<t1<t2<…t_0 < t_1 < t_2 < \dotst0<t1<t2<…
- Irreversibility condition:
- U−1∄(non-invertible updates)U^{-1} \not\exists \quad \text{(non-invertible updates)}U−1∃(non-invertible updates)
- Configuration count:
- Ω=number of stable configurations\Omega = \text{number of stable configurations}Ω=number of stable configurations
- Entropy relation:
- S=kBln⁡ΩS = k_B \ln \OmegaS=kBlnΩ
- Stability-weighted entropy:
- S∼kBln⁡(∑Θ(Σi−Σmin⁡))S \sim k_B \ln \left( \sum \Theta(\Sigma_i - \Sigma_{\min}) \right)S∼kBln(∑Θ(Σi−Σmin))
- Arrow-of-time condition:
- dSdt≥0\frac{dS}{dt} \ge 0dtdS≥0

## Potential Falsifier

- Experimental evidence requiring reversible fundamental dynamics.
- Demonstration that update ordering cannot produce thermodynamic irreversibility.
- Observations incompatible with stability-based entropy scaling.
- Empirical necessity for alternative explanations of time asymmetry.

## Evidence / Notes

- Provides a microscopic origin for thermodynamic time asymmetry.
- Links entropy growth with stability dynamics.
- Conceptually consistent with statistical physics principles.
- Currently speculative; empirical validation requires quantitative modeling.

## Next Action

- Derive thermodynamic laws from node dynamics.
- Compare predictions with statistical physics observations.
- Identify signatures distinguishing QNG entropy behavior.
- Develop simulations illustrating entropy growth and irreversibility.
