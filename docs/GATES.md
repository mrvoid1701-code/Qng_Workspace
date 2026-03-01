# GATES

Gate map for the core GR/QM chain and metric hardening sequence.

| Gate | Brief description | Runner script |
| --- | --- | --- |
| G1 | PPN-gamma consistency on emergent metric (`|gamma-1|` control) | `scripts/run_qng_metric_hardening_v6.py` |
| G2 | `g00` trace-ratio consistency in weak-field metric closure | `scripts/run_qng_metric_hardening_v6.py` |
| G3 | Tidal-fidelity checks (tracelessness, sign consistency, amplitude bound) | `scripts/run_qng_metric_hardening_v6.py` |
| G4 | Weak-field isotropy plausibility (`dev_ratio` control) | `scripts/run_qng_metric_hardening_v6.py` |
| G5 | Dynamics wave propagation test | `scripts/run_qng_dynamics_wave_v1.py` |
| G6 | Spectral analysis gates | `scripts/run_qng_spectrum_v1.py` |
| G7 | Metric dynamics tensorial wave test | `scripts/run_qng_metric_dynamics_v1.py` |
| G8 | Einstein tensor (Forman-Ricci) consistency | `scripts/run_qng_einstein_v1.py` |
| G9 | Emergent energy-momentum conservation | `scripts/run_qng_conservation_v1.py` |
| G10 | Covariant ADM metric construction + weak-field checks | `scripts/run_qng_covariant_metric_v1.py` |
| G11 | Complete Einstein-equation closure checks | `scripts/run_qng_einstein_eq_v1.py` |
| G12 | Known GR solutions sanity (de Sitter + Schwarzschild forms) | `scripts/run_qng_gr_solutions_v1.py` |
| G13 | Covariant metric-wave dynamics | `scripts/run_qng_covariant_wave_v1.py` |
| G14 | Covariant conservation (`âˆ‡_Î¼ T^{Î¼Î½}=0`) | `scripts/run_qng_covariant_cons_v1.py` |
| G15 | PPN parameters (`Î³`, `Î²`) + Shapiro-delay checks (`G15b-v1` legacy radial-shell, `G15b-v2` official potential-quantile) | `scripts/run_qng_ppn_v1.py` |
| G16 | Discrete action functional and Euler-Lagrange closure | `scripts/run_qng_action_v1.py` |
| G17 | Canonical quantization on graph (QM bridge) | `scripts/run_qng_qm_bridge_v1.py` |
| G18 | Quantum information and emergent geometry diagnostics | `scripts/run_qng_qm_info_v1.py` |
| G19 | Unruh thermal vacuum diagnostics | `scripts/run_qng_unruh_thermal_v1.py` |
| G20 | Semiclassical back-reaction loop closure | `scripts/run_qng_semiclassical_v1.py` |

## Notes

- This mapping is implementation-oriented (script-level).
- Historical `QNG-T-*` tests remain tracked in `05_validation/test-plan.md` and `05_validation/results-log.md`.
- `G15b-v2` is the official decision gate for G15b.
- `G15b-v1` remains legacy diagnostic-only (single-peak sanity check).
- GR run summaries expose two chain views:
  - `all_pass_official` (uses `G15b-v2` for decision logic)
  - `all_pass_diagnostic` (legacy chain, keeps `G15` final for diagnostics)
- Effective date for official switch: `2026-03-01` (promotion commit `15dd881`).
- Freeze reference tag: `gr-ppn-g15b-v2-official` (see `docs/CHANGELOG.md`).

