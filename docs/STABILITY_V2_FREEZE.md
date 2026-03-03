# Stability V2 Freeze

Date: 2026-03-03  
Policy: `stability-official-v2`  
Effective tag: `stability-energy-v2-official`

## Axioms (short)

1. Bounded field:
   - `Sigma_i in [0,1]` after each update.
2. Positive metric proxy:
   - diagonal metric proxy remains strictly positive.
3. Local update contract:
   - stability update is local on graph neighborhoods.
4. Fixed governance:
   - formulas and thresholds are frozen unless a new prereg version is created.

## Official Definitions

- State:
  - `Sigma_i`: stability field
  - `chi_i`: memory/load field
  - `phi_i`: phase field
- Official energy gate (v2):
  - decision status uses covariant/Noether-like drift track (`gate_energy_drift_v2`)
  - threshold remains `0.90` (unchanged from v1 governance lane)
- Legacy diagnostic kept:
  - `gate_energy_drift_v1` (raw gate-energy drift)

## Guaranteed vs Observed vs Open

Guaranteed (by policy/tooling):

1. No threshold tuning post-hoc in official switch.
2. Legacy and official statuses are both preserved in summaries.
3. Baseline + regression guard are active for primary/attack/holdout.

Observed (current evidence):

1. Candidate-v2 and official mapping improved energy/all-pass counts with `degraded=0`.
2. Regression guard decision is `PASS` on frozen official-v2 blocks.
3. Convergence gate v1 decision is `PASS` on locked refinement protocol.

Open (explicitly not closed yet):

1. Full theorem-level existence/uniqueness/stability proof in discrete setting.
2. Full convergence proof `discrete -> continuum` (currently contract + empirical gate).
3. Stronger residual-energy consistency coupling beyond current guard checks.
