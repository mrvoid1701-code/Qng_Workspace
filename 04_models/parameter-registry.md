# Parameter Registry

Machine-readable source: `04_models/parameter-registry.json`

## Parameters

| Parameter ID | Symbol | Name | Units | Range | Status | Related claims | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QNG-P-001 | tau | Relaxation Time | s | >= 0 | open | QNG-C-024,QNG-C-038,QNG-C-060,QNG-C-086 | Primary lag parameter in residual/memory dynamics. |
| QNG-P-002 | chi | Straton Load | kg*s/m | >= 0 | open | QNG-C-012,QNG-C-014,QNG-C-073 | Usually chi = m/c. |
| QNG-P-003 | Sigma_min | Stability Threshold | dimensionless | [0,1] | open | QNG-C-004,QNG-C-033 | Persistence threshold for node survival. |
| QNG-P-004 | alpha_tau | Delay Scaling Coefficient | s^2*m/kg | > 0 | open | QNG-C-014 | First-order coefficient in tau(chi). |
| QNG-P-005 | tau_h | Halo Relaxation Timescale | s | > 0 | open | QNG-C-040 | Decay scale for dark-memory halos. |
| QNG-P-006 | beta_q | Threshold Transition Sharpness | dimensionless | > 0 | open | QNG-C-048 | Logistic transition sharpness near threshold. |
| QNG-P-007 | mu_s | Structure Mobility Coefficient | model-dependent | >= 0 | open | QNG-C-107 | Mobility term for accretion flux. |
| QNG-P-008 | k_S | Entropy Normalization Constant | dimensionless | > 0 | provisional | QNG-C-111 | Constant in S(t) = k_S log(Omega). |

## Versioning

- Current version: `1.0.0`
- Last updated: `2026-02-16`
- Change tracking: see `change_log` in the JSON registry.

