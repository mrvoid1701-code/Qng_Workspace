# Symbol Registry

Canonical symbol list for QNG math files.

## Core State Symbols

| Symbol | Meaning | Unit | First usage | Notes |
| --- | --- | --- | --- | --- |
| N_i | Node state tuple | n/a | page-016,page-019,page-071 | Defined as (V_i, chi_i, phi_i). |
| V_i | Discrete node volume | m^3 (or normalized) | page-016,page-019 | Quantized spatial assignment. |
| chi_i | Node informational memory (stratonic load) | kg*s/m | page-016,page-020,page-051 | Local latent load per node. |
| phi_i | Node phase state | rad (or normalized angle) | page-016,page-020,page-071 | Coherence and transition variable. |
| Sigma_i | Node stability score | dimensionless in [0,1] | page-016,page-028,page-072 | Persistence criterion variable. |
| Sigma_min | Stability threshold for persistence | dimensionless | page-016,page-028,page-072 | Node removed if Sigma_i < Sigma_min. |
| U | Update operator | mapping | page-017,page-027,page-072 | N_i(t+1) = U(...). |
| eta_i | Stochastic fluctuation/noise term | model-dependent | page-017,page-027,page-072 | Drives micro fluctuations. |
| Adj(i) | Neighbor set of node i | set | page-072 | Graph adjacency neighborhood. |
| G = (N, E) | Dynamic node graph | graph structure | page-020,page-071,page-072 | Metric-free base topology. |
| Delta_G | Graph Laplacian operator | 1/hop^2 (discrete) | page-073,page-074 | Discrete diffusion/coherence operator. |

## Time and Lag Symbols

| Symbol | Meaning | Unit | First usage | Notes |
| --- | --- | --- | --- | --- |
| t | Discrete update index | integer | page-017,page-072 | Fundamental discrete index. |
| t_R | Reference update time | s | page-023,page-043,page-055,page-073 | Baseline update-clock component. |
| T_C | Composite observed time | s | page-023,page-043,page-045,page-055,page-073 | Effective measured time. |
| tau | Relaxation time / memory delay | s | page-023,page-024,page-036,page-073 | Delay scale for field response. |
| DeltaL | Stratonic lag displacement | m | page-024,page-043,page-073 | DeltaL = v * tau. |
| deltaSigma | Local timing correction from field state | s (effective) | page-045,page-055 | CTM correction term. |
| v | Velocity | m/s | page-024,page-025,page-043,page-063 | Used in lag and residual terms. |

## Field, Force, and Memory Symbols

| Symbol | Meaning | Unit | First usage | Notes |
| --- | --- | --- | --- | --- |
| Sigma(x,t) | Global stability/memory field | dimensionless (model-normalized) | page-024,page-029,page-035,page-060 | Historical field from kernel convolution. |
| nablaSigma | Spatial gradient of stability | 1/m | page-012,page-035,page-088 | Drives emergent gravity behavior. |
| g(x,t) | Emergent gravitational acceleration field | m/s^2 | page-035,page-036,page-073,page-088 | g = -nablaSigma in QNG scaling. |
| F_grav | Emergent force form from stability gradient | N or m/s^2 per unit mass | page-028,page-035 | Often treated as acceleration field. |
| a_res | Residual acceleration from lag | m/s^2 | page-029,page-036,page-040,page-063 | a_res approx -tau (v dot nabla) nablaSigma. |
| a_lag | Lag-induced acceleration term | m/s^2 | page-044,page-052 | Alternative lag parameterization. |
| K(Delta t) | Memory kernel | 1/s (normalized) | page-029,page-035,page-060 | Commonly exponential kernel. |
| rho_chi | Dark-memory density functional | model-dependent | page-052 | Historical chi-weighted density term. |
| T_chi^mu nu | Delayed-response stress tensor extension | same as stress-energy density | page-060 | Effective memory contribution in extended GR form. |

## Emergent and Cosmology Symbols

| Symbol | Meaning | Unit | First usage | Notes |
| --- | --- | --- | --- | --- |
| m | Emergent mass | kg | page-024,page-031,page-051,page-088 | Often linked to temporal stability. |
| a(t) | Emergent scale factor | dimensionless | page-075 | Proposed a(t) proportional to \|N(t)\|^(1/3). |
| \|N(t)\| | Number of active/stable nodes at t | count | page-075 | Node-population measure. |
| S(t) | Entropy-like measure in update space | dimensionless | page-077 | S(t) proportional to log Omega. |
| Omega | Count of stable micro-configurations | count | page-077 | Update-invariant microstate count. |
| Phi(x,t) | Effective coherent field over nodes | model-dependent | page-068 | Used in QFT-like emergence mapping. |
| psi(t) | Emergent wavefunction-like object | complex amplitude | page-068 | Ensemble phase object. |
| Box | Effective d'Alembert operator | 1/m^2 | page-068 | Appears in Klein-Gordon-like form. |

## Constants and Conventions

| Symbol | Meaning | Unit | First usage | Notes |
| --- | --- | --- | --- | --- |
| c | Speed of light | m/s | page-020,page-051,page-088 | Used in chi = m/c. |
| G_N | Newton gravitational constant | m^3/(kg*s^2) | page-067 | Appears in recovered Einstein limit. |
| hbar | Reduced Planck constant | J*s | page-089 | Often normalized with c in theoretical sections. |

## Unit Conventions

- Unless otherwise stated, equations follow SI-inspired units.
- Some sections use normalized theoretical units (for example c = 1, hbar = 1).
- Sigma terms are frequently treated as dimensionless normalized quantities.
- When comparing with data, always restate the active unit convention in the derivation file.
