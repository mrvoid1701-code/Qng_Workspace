# QNG-T-SIG-001 — Generalized Poisson (numeric) prereg

Scope: Numeric check of Newtonian limit on 2D grid with variable metric coupling.

Setup
- Grid: 100×100, domain [-5, 5]², dx = dy = 0.1.
- Source: ρ = M·δ(r), M = 1, G = 1, α = 4π. Implemented as a single cell at center with mass / (dx·dy).
- Boundary: Dirichlet Σ = 0 on boundary.
- Initial metric g₀ = I.
- Iterations: up to 50.
- Update loop per iteration n:
  1) Solve ∂i(gₙ^{ij} ∂j Σₙ) = 4πρ (variable-coefficient Poisson).
  2) Compute Hessian H(Σₙ); set gₙ₊₁ = SPD_normalize(-H) (eigen clip min=1e-3).
  3) Stop if ||gₙ₊₁−gₙ||_F / ||gₙ||_F < 1e-2.

Gates
- G1 (Newton residual): p90(|∇²Σ − 4πρ| / (4π·ρ_max)) < 0.10.
- G2 (metric convergence, T-SIG-002): reached ||gₙ₊₁−gₙ||_F / ||gₙ||_F < 0.01 within ≤50 iters.
- FINAL: pass if G1 and G2 both pass.

Outputs
- gate_summary.csv
- convergence_history.csv (per iter: iter, rel_change_g, max_residual)
- sigma_field.png, residual_map.png
- run-log.txt (params)

Anti-tuning
- Thresholds fixed here; any change => new prereg (qng-t-sig-001-v2).***
