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
| G14 | Covariant conservation (`nabla_mu T^{mu nu}=0`) | `scripts/run_qng_covariant_cons_v1.py` |
| G15 | PPN parameters (`gamma`, `beta`) + Shapiro-delay checks (`G15b-v1` legacy radial-shell, `G15b-v2` official potential-quantile) | `scripts/run_qng_ppn_v1.py` |
| G16 | Discrete action functional and Euler-Lagrange closure | `scripts/run_qng_action_v1.py` |
| G17 | Canonical quantization on graph (QM bridge; `G17a-v4 + G17b-v6` official policy, `G17-v1` legacy diagnostic) | `scripts/run_qng_qm_bridge_v1.py` |
| G18 | Quantum information and emergent geometry diagnostics (`G18d-v7 + G18b-v8` official decision layer) | `scripts/run_qng_qm_info_v1.py` |
| G19 | Unruh thermal vacuum diagnostics (`G19d-v4` official decision layer) | `scripts/run_qng_unruh_thermal_v1.py` |
| G20 | Semiclassical back-reaction loop closure | `scripts/run_qng_semiclassical_v1.py` |
| G21 | Thermodynamic consistency (S≥0, C_V>0, F=U-TS, S(2T)/S(T)>1.5) | `scripts/run_qng_g21_thermo_v1.py` |
| G22 | Directional isotropy: d_s consistent across spectral axes (partial Lorentz test) | `scripts/run_qng_g22_isotropy_v1.py` |
| G23 | Klein-Gordon scalar matter field: Yukawa decay + spectral gap on Jaccard graph | `scripts/run_qng_g23_klein_gordon_v1.py` |
| G24 | Spectral foliation & time direction: Fiedler vector + 3+1 structure (v1) | `scripts/run_qng_g24_foliation_v1.py` |
| G24v2 | Temporal gradient foliation: quintile Fiedler → d_s_equatorial=3.07, 3+1 evidence | `scripts/run_qng_g24_v2_foliation_v1.py` |
| G25 | UV running of spectral dimension: d_s_UV≈3.0 vs d_s_IR≈4.4 (prediction vs CDT/LQG/AS) | `scripts/run_qng_g25_uv_running_v1.py` |
| G26 | CMB Planck observational gate: ell_damp(0.17σ), n_s(0.83σ), Δχ²_rel=−371, ℓ_A spacing(5.7%) — 4/4 PASS | `scripts/run_qng_g26_cmb_v1.py` |
| G27 | K_R universality: k=0.835–0.850 pe 18 ordine de mărime (Gpc→pc), spread 1.80% — 4/4 PASS | `scripts/run_qng_g27_kr_universality_v1.py` |

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
  - `G11` official uses candidate-v5 decision status
  - `G12` official uses candidate-v5 decision status
  - `G7/G8/G9` remain inherited unchanged
  - runner: `scripts/tools/run_gr_stage3_official_v3.py`
  - effective tag: `gr-stage3-g11-v5-official`
- Stage-3 official switch record:
  - `docs/GR_STAGE3_OFFICIAL_SWITCH.md` (v2, historical)
  - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md` (v3, historical)
  - `docs/GR_STAGE3_G11_V5_OFFICIAL_SWITCH.md` (v5, current)
- Stage-2 official switch records:
  - v2: `docs/GR_STAGE2_OFFICIAL_SWITCH.md`
  - v3: `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md`
  - v4: `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`
- QM Stage-1 official decision policy (governance-layer mapping on frozen runs):
  - `G17` official uses `G17a-v4 + G17b-v6` decision status
  - `G18` official uses `G18d-v7` + `G18b-v8` decision status
  - `G19` official uses candidate-v4 decision status (`G19d-v4`, high-signal median + local-window fallback in multi-peak regimes)
  - `G17-v1` and `G18-v1` remain legacy diagnostic-only
  - `G20` remains inherited unchanged
  - runner: `scripts/tools/run_qm_stage1_official_v4.py` (policy id `qm-stage1-official-v14`)
  - effective tag: `qm-stage1-g19-v4-official`
- QM Stage-1 official switch records:
  - `docs/QM_STAGE1_G17_V2_OFFICIAL_SWITCH.md` (historical, v2)
  - `docs/QM_STAGE1_G18_V2_OFFICIAL_SWITCH.md` (historical, v3)
  - `docs/QM_STAGE1_G17_V3_OFFICIAL_SWITCH.md` (historical, v4)
  - `docs/QM_STAGE1_G18_V3_OFFICIAL_SWITCH.md` (historical, v5)
  - `docs/QM_STAGE1_G17B_V4_OFFICIAL_SWITCH.md` (historical, v6)
  - `docs/QM_STAGE1_G18_V4_OFFICIAL_SWITCH.md` (historical, v7)
  - `docs/QM_STAGE1_G18_V5_OFFICIAL_SWITCH.md` (historical, v8)
  - `docs/QM_STAGE1_G18_V6_OFFICIAL_SWITCH.md` (historical, v9)
  - `docs/QM_STAGE1_G17A_V4_OFFICIAL_SWITCH.md` (historical, v10)
  - `docs/QM_STAGE1_G18_V7_G19_V2_OFFICIAL_SWITCH.md` (historical, v11)
  - `docs/QM_STAGE1_G17B_V6_OFFICIAL_SWITCH.md` (historical, v12)
  - `docs/QM_STAGE1_G18B_V8_OFFICIAL_SWITCH.md` (historical, v13)
  - `docs/QM_STAGE1_G19_V4_OFFICIAL_SWITCH.md` (current, v14)
- `QM-Stage-1` freeze contract:
  - `docs/QM_STAGE1_FREEZE.md`
- `QM-Stage-2` prereg lane (candidate-only, not official):
  - `docs/QM_STAGE2_PREREG.md`
  - orchestration: `scripts/tools/run_qm_stage2_prereg_v1.py`
- QM decision criteria are tracked in a separate lane: `docs/QM_LANE_POLICY.md`.
- QM-Stage-1 prereg source: `05_validation/pre-registrations/qm-stage1-prereg-v1.md`.
- Stability lane official decision policy:
  - legacy energy gate: `gate_energy_drift_v1`
  - official energy gate: `gate_energy_drift_v2` (mapped as `gate_energy_drift`)
  - legacy all-pass: `all_pass_v1`
  - official all-pass: `all_pass_v2` (mapped as `all_pass_stability`)
  - runner: `scripts/tools/run_stability_official_v2.py`
  - effective tag: `stability-energy-v2-official`
- Stability convergence lane official decision policy:
  - official convergence gate: `scripts/tools/run_stability_convergence_gate_v6.py`
  - legacy comparator (diagnostic only): `v5-like` (`run_stability_convergence_gate_v4.py` + v5 frozen constants)
  - baseline builder: `scripts/tools/build_stability_convergence_v6_baseline_v1.py`
  - regression guard: `scripts/tools/run_stability_convergence_v6_regression_guard_v1.py`
  - effective tag: `stability-convergence-v6-official`
- Stability official switch record:
  - `docs/STABILITY_ENERGY_V2_OFFICIAL_SWITCH.md`
  - `docs/STABILITY_CONVERGENCE_V6_OFFICIAL_SWITCH.md`
- Stability freeze/contract docs:
  - `docs/STABILITY_V2_FREEZE.md`
  - `docs/STABILITY_DUAL_CHANNELS.md`
  - `docs/STABILITY_CONVERGENCE_V6_LOCK_IN.md`
  - `05_validation/pre-registrations/qng-stability-convergence-v1.md`
  - `05_validation/pre-registrations/qng-stability-convergence-v2.md`

