# QNG-C-019

- Status: derived
- Confidence: medium
- Source page(s): page-020
- Related derivation: 03_math/derivations/qng-c-019.md
- Register source: 02_claims/claims-register.md

## Claim Statement

Spatial distance is defined by the shortest-path length within the node graph, while curvature is encoded in the local topological structure and connectivity variations of the graph rather than in an embedded geometric manifold.

## Assumptions

- A1. Nodes and edges form a relational graph representing fundamental spatial structure.
- A2. Physical adjacency and separation are determined by graph connectivity.
- A3. Macroscopic geometric quantities emerge from coarse-grained graph properties.
- A4. Variations in local connectivity correspond to effective curvature.
- A5. Observable geometric behavior depends only on relational structure, not on embedding coordinates.

## Mathematical Form

- Shortest-path distance:
- d(i,j)=min⁡Pij∑(k,l)∈Pijwkld(i,j) = \min_{P_{ij}} \sum_{(k,l)\in P_{ij}} w_{kl}d(i,j)=Pijmin(k,l)∈Pij∑wkl
- where PijP_{ij}Pij is a path between nodes iii and jjj, and wklw_{kl}wkl are edge weights.
- Topological curvature indicator (generic form):
- Ki∼F(local connectivity,cycle structure,degree distribution)K_i \sim F(\text{local connectivity}, \text{cycle structure}, \text{degree distribution})Ki∼F(local connectivity,cycle structure,degree distribution)
- Graph Laplacian representation:
- L=D−AL = D - AL=D−A
- where AAA is the adjacency matrix and DDD is the degree matrix.
- Continuum correspondence:
- G→coarse-grain(M,gμν)G \xrightarrow{\text{coarse-grain}} (\mathcal{M}, g_{\mu\nu})Gcoarse-grain(M,gμν)

## Potential Falsifier

- Experimental evidence requiring distance measures incompatible with any graph-based shortest-path representation.
- Observations showing curvature independent of relational topology.
- Demonstration that geometric effects cannot be reproduced by connectivity variations in discrete networks.
- Empirical necessity for embedding geometry beyond relational structure.

## Evidence / Notes

- Conceptually consistent with network-based geometry and discrete spacetime models.
- Analogous to geometric properties emerging from lattice and graph structures.
- Provides a mechanism for curvature without requiring continuous manifolds.
- Empirical validation depends on recovering known geometric predictions from graph dynamics.

## Next Action

- Derive effective curvature tensors from graph connectivity statistics.
- Demonstrate recovery of General Relativity geodesics from shortest-path dynamics.
- Simulate geometric behavior in evolving node networks.
- Identify observable deviations from continuum curvature models.
