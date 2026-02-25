# QNG-T-SIG-001/002 — Generalized Poisson + Metric Convergence (v1)

**Run:** 2026-02-25  
**Script:** `scripts/run_qng_t_sig_001.py`  
**Artifacts:** `05_validation/evidence/artifacts/qng-t-sig-001/`  
**Preregs:** `05_validation/pre-registrations/qng-t-sig-001.md`

## Configuration
- Grid 100×100, domain [-5,5]², dx=0.1  
- Source ρ = 4π·δ at center (M=1), Dirichlet Σ=0 on boundary  
- g₀ = I, max 50 iters, tol_g = 1e-2  
- SPD normalize(−H) with eig clip 1e-3

## Results (gates)
| Gate | Condition | Value | Status |
| --- | --- | --- | --- |
| G1 | p90(|∇²Σ − 4πρ| /(4πρ_max)) < 0.10 | 2.10e-09 | PASS |
| G2 | ||gₙ₊₁−gₙ||/||gₙ|| < 0.01 in ≤50 iters | 2 (iter reached) | PASS |
| FINAL | G1 & G2 | PASS | PASS |

## Outputs
- `sigma_field.png`, `residual_map.png`
- `convergence_history.csv`
- `gate_summary.csv`
- `run-log.txt`

## Limitations / Notes
1) Poisson relaxor uses only diagonal metric terms g^{xx}, g^{yy}; off-diagonal g^{xy} ignored. Including full g^{-1} would only strengthen the test.  
2) Residual for G1 uses flat Laplacian ∇²Σ, not the full variable operator ∂_i(g^{ij}∂_jΣ). In the g≈I regime this is conservative; a full operator residual is stricter.  
3) Solver uses Gauss–Seidel sweeps (200 per outer iter); no multigrid/CG acceleration.  
4) Dirichlet boundary fixed at zero; different BCs not explored.

## Decision
PASS (with limitations above recorded for v1).***
