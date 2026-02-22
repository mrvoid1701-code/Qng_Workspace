# QNG-C-003

- Status: formalized
- Confidence: high
- Source page(s): page-017
- Related derivation: n/a
- Register source: 02_claims/claims-register.md

## Claim Statement

Time is not a fundamental geometric dimension but emerges as the ordered sequence of state updates in the discrete node network, representing causal progression rather than an independent coordinate.

## Assumptions

- A1. The fundamental dynamics of the system are governed by discrete update operations applied to node states.
- A2. Causality is defined by the order of updates rather than by embedding in a continuous temporal manifold.
- A3. Observable temporal intervals correspond to accumulated update processes within physical systems.
- A4. Apparent continuous time arises from coarse-graining over large numbers of discrete updates.
- A5. Physical evolution is irreversible at the fundamental level due to non-invertible update dynamics and stochastic fluctuations.

## Mathematical Form

- Discrete update sequence:
- Ni(t+1)=U ⁣(Ni(t),{Nj(t)}j∈Neighbors(i),ηi(t))N_i(t+1) = U\!\left(N_i(t), \{N_j(t)\}_{j \in \text{Neighbors}(i)}, \eta_i(t)\right)Ni(t+1)=U(Ni(t),{Nj(t)}j∈Neighbors(i),ηi(t))
- Temporal ordering:
- T≡{t0,t1,t2,… },tk+1>tkT \equiv \{t_0, t_1, t_2, \dots\}, \quad t_{k+1} > t_kT≡{t0,t1,t2,…},tk+1>tk
- Observable time (composite form):
- Tobs=f(update count,χ,τ,Σ)T_{\text{obs}} = f(\text{update count}, \chi, \tau, \Sigma)Tobs=f(update count,χ,τ,Σ)
- Continuum limit:
- Δt→0⇒T→R\Delta t \rightarrow 0 \quad \Rightarrow \quad T \rightarrow \mathbb{R}Δt→0⇒T→R
- where continuous time emerges as an effective approximation.

## Potential Falsifier

- Experimental confirmation that time is a fundamental geometric dimension independent of physical processes.
- Observations requiring perfectly continuous temporal evolution without any discrete substrate.
- Evidence of reversible fundamental temporal dynamics incompatible with ordered update processes.
- Detection of phenomena that require time to exist independently of state evolution (i.e., evolution without change).

## Evidence / Notes

- Conceptually consistent with computational and causal models of physics (cellular automata, causal sets).
- Compatible with thermodynamic arrow of time emerging from irreversible processes.
- Aligns with interpretations where time is relational or emergent from dynamics rather than fundamental.
- No direct experimental confirmation currently exists; support is theoretical and conceptual.

## Next Action

- Derive relativistic time dilation as an emergent effect of update dynamics.
- Connect update rate to measurable physical parameters (e.g., τ, χ).
- Identify observable consequences of discrete temporal structure (e.g., noise signatures, timing limits).
- Develop simulations demonstrating emergence of continuous temporal behavior from discrete updates.
