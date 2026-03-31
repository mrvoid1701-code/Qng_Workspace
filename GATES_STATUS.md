# QNG Gate Suite — Status Dashboard

**Dataset:** DS-002 (n=280 nodes, k=8, seed=3401)
**Last run:** 2026-03-04
**Result: 11/11 PASS**

> Legacy snapshot note:
> This dashboard is an older DS-002 2D-style snapshot kept for audit history.
> Official operational status is the Jaccard/4D freeze package:
> `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/` (including `metric_snapshot.csv` and `summary.json`).
> In that official lane, `G18d` is tracked at `d_s=4.082091` with threshold `(3.5, 4.5)` and `PASS`.

---

## Gate Health Table

| Gate | Label | Script | Key metric | Value | Threshold | Margin | Status |
|------|-------|--------|-----------|-------|-----------|--------|--------|
| G10 | Covariant ADM metric | run_qng_covariant_metric_v1.py | min_N | 0.900 | >0.0 | ∞ | ✓ |
| G10 | | | max_abs_Phi | 0.100 | <0.5 | 80% | ✓ |
| G10 | | | min_gamma | 1.010 | >0.0 | ∞ | ✓ |
| G10 | | | mean_a_radial | 0.017 | >0.0 | ∞ | ✓ |
| G11 | Einstein equations | run_qng_einstein_eq_v1.py | hamiltonian_R2 | 0.057 | >0.02 | 185% | ✓ |
| G11 | | | slope_abs_B | 1.804 | >0.260 | 594% | ✓ |
| G11 | | | bianchi_ratio | 0.288 | <1.5 | 81% | ✓ |
| G11 | | | max_trace_G | 8.9e-16 | <1e-10 | ∞ | ✓ |
| G12 | GR solutions | run_qng_gr_solutions_v1.py | — | — | — | — | ✓ |
| G13 | Covariant wave | run_qng_covariant_wave_v1.py | — | — | — | — | ✓ |
| G14 | Conservation ∇T=0 | run_qng_covariant_cons_v1.py | — | — | — | — | ✓ |
| G15 | PPN parameters | run_qng_ppn_v1.py | — | — | — | — | ✓ |
| G16 | Action S[g,σ] | run_qng_action_v1.py | hessian_frac_neg | 1.000 | >0.9 | **11.1%** | ✓ ⚠ |
| G17 | QM bridge | run_qng_qm_bridge_v1.py | spectral_gap μ₁ | 0.01109 | >0.01 | **10.9%** | ✓ ⚠ |
| G17 | | | propagator_slope | −0.01367 | <−0.01 | 36.7% | ✓ |
| G17 | | | E0_per_mode | 0.1764 | (0.05, 5.0) | 252% | ✓ |
| G17 | | | heisenberg_dev | 0.000000 | <0.01 | ∞ | ✓ |
| G18 | QM info & geometry | run_qng_qm_info_v1.py | entropy_SA | 13.13 | >6.58 | 99.5% | ✓ |
| G18 | | | n_IPR | 3.962 | <5.0 | 20.8% | ✓ |
| G18 | | | cv_Gii | 0.259 | <0.50 | 48.2% | ✓ |
| G18 | | | spectral_dim_ds | 4.082 | (3.5, 4.5) | 83.6% | ✓ |
| G19 | Unruh thermal | run_qng_unruh_thermal_v1.py | cv_T_unruh | 0.438 | >0.05 | 776% | ✓ |
| G19 | | | EMB_over_EBE | 778 | >2.0 | ∞ | ✓ |
| G19 | | | ratio_2T | 39.5 | >3.0 | ∞ | ✓ |
| G19 | | | dG_slope | −3.85e-5 | <−1e-5 | 285% | ✓ |
| G20 | Semiclassical | run_qng_semiclassical_v1.py | energy_err | 0.000000 | <0.01 | ∞ | ✓ |
| G20 | | | cv_eps_vac | 0.414 | >0.05 | 728% | ✓ |
| G20 | | | dE0_rel | 0.00426 | (1e-5, 0.3) | 41500% | ✓ |
| G20 | | | max_residual | 0.026 | <0.20 | 87% | ✓ |
| G21 | Thermodynamics | run_qng_g21_thermo_v1.py | S_total | 2.36e-6 | >1e-8 | 23500% | ✓ |
| G21 | | | C_V | 4.08e-5 | >1e-12 | ∞ | ✓ |
| G21 | | | id_error | 1.31e-16 | <1e-8 | ∞ | ✓ |
| G21 | | | S_ratio_2T | 5542 | >1.5 | 369333% | ✓ |

---

## Fragile Metrics (margin < 20%)

| Gate | Metric | Value | Threshold | Margin | Note |
|------|--------|-------|-----------|--------|------|
| G16d | hessian_frac_neg | 1.000 | >0.9 | 11.1% | Hessian fully negative-definite; stable but watch if graph changes |
| G17a | spectral_gap μ₁ | 0.01109 | >0.01 | 10.9% | Lowest non-trivial eigenvalue of −L_rw; monitor at alternative seeds |
| G18d | spectral_dim d_s | 4.082 | (3.5, 4.5) | 83.6% | Official Jaccard/4D lane target; legacy 2D threshold retained only in archived snapshots |

---

## Physics Summary

The gate chain G10→G21 traces the full QNG derivation:

| Gates | Physics layer | Key result |
|-------|--------------|------------|
| G10–G12 | Emergent GR (metric, Einstein eqs, Schwarzschild) | Discrete Ricci flow converges to smooth metric |
| G13–G14 | Field propagation (wave eq, ∇T=0) | Conservation holds to machine precision |
| G15 | Post-Newtonian limit | γ=1, β=1, Shapiro delay match GR |
| G16 | Variational principle | Action S[g,σ] extremized; Hessian fully negative-definite |
| G17 | Canonical quantization | Spectral gap > 0; Heisenberg saturated exactly (Δσ·Δπ = 0.5) |
| G18 | Quantum information | Entanglement entropy S_A=13.1 bits; official Jaccard lane spectral dim d_s≈4.08 |
| G19 | Unruh effect | T_Unruh varies across graph; Bose-Einstein vs Maxwell-Boltzmann ratio=778 |
| G20 | Back-reaction | Semiclassical α¹ = α⁰·(1+λf); δE₀/E₀ = λ/2·cv² verified analytically |
| G21 | Thermodynamics | S≥0, C_V>0, F=U−TS (err=1.3e-16), S(2T)/S(T)=5542 — sistem termodinamic stabil |

---

## Running the Suite

```bash
# Read-only: check existing artifacts
python run_all_gates.py --no-run

# Run all gates (takes ~30s for G17-G20)
python run_all_gates.py

# Run fast gates only (G10-G16, ~5s)
python run_all_gates.py --fast

# Run a single gate
python run_all_gates.py --gate G17
```

Outputs: `gates_summary.csv`, `gates_summary.txt`, `gates_all_pass.flag` (CI sentinel).

---

## Script Archive

Superseded scripts moved to `scripts/_archive/`:
- `run_qng_metric_hardening_v1–v6.py` — iterative hardening iterations
- `run_qng_metric_gr_bridge_v1–v2.py` — bridge prototypes
- `run_qng_conservation_v1.py`, `run_qng_einstein_v1.py`, etc. — early drafts
- `run_qng_t_*.py` — standalone test experiments (T-001 to T-053 series)

---

## Governance Freeze Update (2026-03-10)

Jaccard lane operational freeze is now active via:

- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/summary.json`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/manifest.json`
- `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/latest_check/regression_report.json`

Operational commands:

```bash
make qng_jaccard_freeze_v1
make qng_jaccard_regression_guard_v1
```

Current frozen status:

- Gates included: `G10..G21`
- Snapshot decision: `ALL PASS`
- Guard decision: `PASS` (`missing=0`, `degraded=0`)
