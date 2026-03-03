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
| G17 | Canonical quantization on graph (QM bridge; `G17-v2` official, `G17-v1` legacy diagnostic) | `scripts/run_qng_qm_bridge_v1.py` |
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
- `G16b` official decision gate uses frozen hybrid policy:
  - low-signal (`std(T11)/|mean(T11)| > 10`) -> `G16b-v2`
  - high-signal -> `G16b-v1`
- `G16b-v1` remains legacy diagnostic baseline.
- `G16b-v2` remains candidate diagnostic component (used by official hybrid only in low-signal regime).
- Effective date for `G16b` official hybrid switch: `2026-03-02`.
- Freeze reference tags: `gr-ppn-g15b-v2-official`, `pre-g16b-hybrid-official`, `gr-g16b-hybrid-official` (see `docs/CHANGELOG.md`).
- Stage-2 official decision policy (governance-layer mapping on frozen runs):
  - `G11` official uses `G11a-v4` fallback (robust rank high-signal rule)
  - `G12` official keeps frozen `G12d-v2` status (unchanged)
  - runner: `scripts/tools/run_gr_stage2_official_v4.py`
  - effective tag: `gr-stage2-g11-v4-official`
- `GR-Stage-1` freeze contract: `docs/GR_STAGE1_FREEZE.md`.
- `GR-Stage-2` prereg expansion lane (strong-field + 3+1 + tensor): `docs/GR_STAGE2_PREREG.md`.
- `GR-Stage-3` prereg extension lane (adds geometry + conservation checks): `docs/GR_STAGE3_PREREG.md`.
- Stage-3 official decision policy (governance-layer mapping on frozen runs):
  - `G11` official uses candidate-v3 decision status
  - `G12` official uses candidate-v3 decision status
  - `G7/G8/G9` remain inherited unchanged
  - runner: `scripts/tools/run_gr_stage3_official_v3.py`
  - effective tag: `gr-stage3-g11g12-v3-official`
- Stage-3 official switch record:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md` (v2, historical)
  - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md` (v3, current)
- Stage-2 official switch records:
  - v2: `docs/GR_STAGE2_OFFICIAL_SWITCH.md`
  - v3: `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md`
  - v4: `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`
- QM Stage-1 official decision policy (governance-layer mapping on frozen runs):
  - `G17` official remains inherited from prior official-v2 governance output
  - `G18` official uses candidate-v2 decision status (`G18d-v2`)
  - `G17-v1` and `G18-v1` remain legacy diagnostic-only
  - `G19/G20` remain inherited unchanged
  - runner: `scripts/tools/run_qm_stage1_official_v3.py`
  - effective tag: `qm-stage1-g18-v2-official`
- QM Stage-1 official switch records:
  - `docs/QM_STAGE1_G17_V2_OFFICIAL_SWITCH.md` (historical, v2)
  - `docs/QM_STAGE1_G18_V2_OFFICIAL_SWITCH.md` (current, v3)
- QM decision criteria are tracked in a separate lane: `docs/QM_LANE_POLICY.md`.
- QM-Stage-1 prereg source: `05_validation/pre-registrations/qm-stage1-prereg-v1.md`.

