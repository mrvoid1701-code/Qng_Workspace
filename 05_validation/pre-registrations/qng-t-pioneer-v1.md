# QNG-T-PIONEER-v1 — prereg (Pioneer anomaly)

Data/target:
- Measured Pioneer anomaly: a_P = (8.74 ± 1.33) × 10⁻¹⁰ m/s² (Anderson et al. 2002, PRD).
- Radial domain: 20–70 AU (Pioneer 10/11 cruise).

Model assumption (v1):
- QNG correction in weak-field, flat metric: a_QNG(r) = τ_flyby · |∇Σ| with Σ = −GM☉/r.
- τ_flyby fixed to value calibrated on flyby test T-028 (v4).
- Metric assumed near-flat so g^{ij} ≈ δ^{ij}.

Gates:
- G1: a_QNG(r) ∈ [6.0e-10, 1.1e-9] m/s² for r ∈ [20, 70] AU (using τ_flyby from T-028).
- G2 (negative control): for inner planets (Mercury 0.39 AU, Venus 0.72 AU), a_QNG < 1.0e-12 m/s².
- FINAL: pass iff G1 and G2 both pass.

Evidence to produce:
- gate_summary.csv
- pioneer_prediction.csv with columns (r_AU, a_qng)
- inner_control.csv with (body, r_AU, a_qng)
- run-log.txt (τ used, constants, gates, decision)

Notes:
- If τ_flyby is updated, this prereg becomes invalid; create v2.
- If a more complete lag term (e.g., directional or anisotropy factors) is introduced, prereg v2 required.***
