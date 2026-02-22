# QNG-C-077

- Status: formalized
- Confidence: medium
- Source page(s): page-056
- Related derivation: 03_math/derivations/qng-c-077.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Causality in QNG is defined by directed state-dependency relations between nodes, represented as edges in the update graph, such that causal structure emerges from dependency constraints rather than from an external spacetime background.

## Assumptions

- A1. Node evolution occurs through discrete update rules.
- A2. State changes depend only on local neighborhood information and prior states.
- A3. Dependency relations define allowed propagation of influence.
- A4. Global causal structure emerges from local dependency constraints.
- A5. Observable causality corresponds to coarse-grained behavior of the update graph.

## Mathematical Form

- Graph representation:
- G=(N,E)G = (N, E)G=(N,E)
- Directed dependency edge:
- (i→j)∈E⇒Nj(t+1)=Uj(Nj(t),Ni(t),… )(i \rightarrow j) \in E \quad \Rightarrow \quad N_j(t+1) = U_j(N_j(t), N_i(t), \dots)(i→j)∈E⇒Nj(t+1)=Uj(Nj(t),Ni(t),…)
- Causal reachability:
- i≺jif a directed path exists from i to ji \prec j \quad \text{if a directed path exists from } i \text{ to } ji≺jif a directed path exists from i to j
- Light-cone analogue:
- C(i,t)={j∣i≺j within Δt}\mathcal{C}(i,t) = \{ j \mid i \prec j \text{ within } \Delta t \}C(i,t)={j∣i≺j within Δt}
- Locality constraint:
- Ui depends only on neighbors of iU_i \text{ depends only on neighbors of } iUi depends only on neighbors of i

## Potential Falsifier

- Experimental evidence requiring causality independent of state-dependency relations.
- Observations incompatible with graph-based causal propagation.
- Demonstration that dependency-defined causality cannot reproduce relativistic causal structure.
- Empirical necessity for external spacetime causality without network mediation.

## Evidence / Notes

- Provides a relational definition of causality consistent with discrete network dynamics.
- Conceptually compatible with causal-set and graph-based physics approaches.
- Allows emergence of effective causal cones from local update rules.
- Empirical validation depends on reproducing known relativistic causality behavior.

## Next Action

- Derive effective causal speed limits from update rules.
- Compare emergent causal structure with relativistic light cones.
- Simulate propagation of information in the update graph.
- Identify observational consequences of dependency-based causality.
