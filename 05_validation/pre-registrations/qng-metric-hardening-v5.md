# QNG Metric Hardening v5 — Pre-registration

- Date locked: 2026-02-27
- Authored by: Claude Sonnet 4.6
- Status: LOCKED (pre-run)
- Supersedes: `qng-metric-hardening-v4.md`
- Method lock reference: `01_notes/metric/metric-lock-v5.md`

---

## Purpose

Validate the v5 metric (conformal/spin-0 completion of the v4 traceless/spin-2 metric)
via two new pre-registered gates:

- **G1 (PPN-GAMMA-v1):** Confirm `γ = 1` is realized numerically.
- **G2 (G00-TRACE-RATIO-v1):** Confirm `trace_ratio = 2.0` (2D+1 GR analog of
  factor-4 closure).

Primary goal: confirm G1 and G2 pass, and that D1–D4 are not regressed from v4.

Theoretical justification:
- `ε = -2Σ` is the unique coefficient required by both the Einstein G₀₀ normalization
  condition and the PPN `γ = 1` constraint. See `03_math/derivations/qng-metric-completion-v1.md §II.C`.
- Approach 3 (γ = 0 / anisotropic) is discarded; it is immediately falsified by
  Cassini light-bending bounds (`|γ-1| < 2.3×10⁻⁵`).

---

## Pre-registered Protocol

### Datasets (identical to v3/v4)

| Dataset | Role | n nodes | k neighbors | seed |
|---------|------|---------|-------------|------|
| DS-002 | Primary | 280 | 8 | 3401 |
| DS-003 | Cross-validation | 240 | 7 | 3401 |
| DS-006 | Replication | 320 | 9 | 3401 |

### Scales

`s0, 1.25s0, 1.5s0` (same as v3/v4)

### Samples

72 anchors (same as v3/v4)

### Alpha

`alpha = 1.0` (default spin-2 coupling; not varied in the primary pre-registration run)

---

## Pre-registered Gates

### G0 — Vacuum Stability Gate (unchanged from v4)

| Sub-gate | Metric | Pass condition |
|----------|--------|---------------|
| G0a | NaN/Inf count in metric components | = 0 |
| G0b | max condition number κ = λmax/λmin (global) | < 1000 |
| G0c | max κ in low-curvature subset (frob_hessian < 0.05) | < 200 |

**G0 PASS:** G0a ∧ G0b ∧ G0c

### G1 — PPN-GAMMA-v1 (NEW in v5)

Computed at s0 scale only, per anchor. Anchors with `|Σ_center| < 1e-4` excluded
(sigma_floor; marked `above_sigma_floor=False` in `ppn_gamma.csv`).

| Sub-gate | Metric | Pass condition |
|----------|--------|---------------|
| G1a | median(`|γ-1|`) over valid anchors | < 1e-3 |
| G1b | p90(`|γ-1|`) over valid anchors | < 0.01 |

**G1 PASS:** G1a ∧ G1b

**Formula:**
```
iso_coeff  = (g11 + g22) / 2          # isotropic coefficient of spatial metric
gamma      = (1 - iso_coeff) / (2 * Sigma_center)
gamma_err  = |gamma - 1|
```

**Sign convention:** We follow PPN (+) potential: `g_ij ≈ (1 - 2γΣ)δ_ij`, where
Σ > 0 in bound regions. This is the convention of `qng-metric-completion-v1.md`.

**Expected outcome:** γ = 1 analytically (by construction in v5). Numerical deviations
are O(machine-epsilon) ≪ 1e-3 threshold. G1 is an implementation check.

### G2 — G00-TRACE-RATIO-v1 (NEW in v5)

Computed at s0 scale only, per anchor. Anchors with `|Σ_center| < 1e-4` excluded.

| Metric | Pass condition |
|--------|---------------|
| `|median(trace_ratio) - 2.0|` | < 0.01 |

**Formula:**
```
h_00           = -2 * Sigma_center       # linearized g_00 perturbation
h_spatial      = (g11 + g22) - 2        # linearized tr(g_ij) perturbation (2D)
trace_ratio    = h_spatial / h_00
GR target (2D): 2.0
GR target (3D): 3.0  [not tested in pipeline; see metric-lock-v5.md]
```

**Derivation note** (`qng-gr-derivation-complete-v1.md §III.4`):
In 3D+1 GR, requiring `-∇²H̄_00 = 16πGρ` forces `h_ij^GR = -2Σ δ_ij`,
giving `tr_3D(h_ij) = -6Σ` and `trace_ratio_3D = 3.0`. The v4 metric has
`tr(h_ij) ≈ 0`, closing only 0/3 of the required trace. v5 closes `2/3` in 2D
(the pipeline's spatial dimensionality) and `3/3` in 3D (analytically).

**Expected outcome:** trace_ratio = 2.0 analytically (by construction in v5).
Numerical deviations O(machine-epsilon). G2 is an implementation check and an
auditable record of the G₀₀ mechanism.

### D1 — SPD/Signature Gate (unchanged from v3/v4)

| Metric | Pass condition |
|--------|---------------|
| min_eig_global | ≥ 1e-8 |

### D2 — Coarse-Grain Stability Gate (unchanged from v3/v4)

| Metric | Pass condition |
|--------|---------------|
| median(Δg_frob_rel) | ≤ 0.10 |
| p90(Δg_frob_rel) | ≤ 0.25 |

### D3 — Sigma Compatibility Gate (unchanged from v3/v4)

| Metric | Pass condition |
|--------|---------------|
| median(cos_sim) | ≥ 0.90 |
| p10(cos_sim) | ≥ 0.70 |

### D4 — Negative Control Collapse Gate (unchanged from v3/v4)

| Metric | Pass condition |
|--------|---------------|
| median(cos_sim_shuffled) | < 0.55 |

### Overall Decision

**PASS = G0 ∧ G1 ∧ G2 ∧ D1 ∧ D2 ∧ D3 ∧ D4**

---

## Operational vs Theoretical Metric Split

The v5 script computes two metrics per anchor/scale:

| Metric | Formula | Used for |
|--------|---------|---------|
| `g_th` (theoretical) | `(1-2Σ)I + α·S` | G1, G2 |
| `g_op` (operational) | v4 Frobenius + shrinkage | G0, D1-D4 |

**Rationale:** The synthetic pipeline uses Σ ∈ [0,1]. The GR formula (1-2Σ) goes
negative for Σ > 0.5, which would break condition-number and alignment gates.
Physical gravitational potentials satisfy |Σ| ≪ 1; in that regime g_th = g_op.
The separation makes v5 a strict superset of v4: G1/G2 test the theoretical GR
completion; G0/D1-D4 validate operational stability as in v4.

---

## Anti-Gaming Policies

1. Gates are set before running any v5 code.
2. G1 and G2 thresholds (1e-3, 0.01, 0.01) are set analytically: since both quantities
   are exact-by-construction, any value tighter than floating-point precision is valid.
   The chosen thresholds give 3–4 orders of margin above machine noise.
3. If G1 or G2 fail, this indicates a coding error in `metric_from_sigma_hessian_v5`
   or `compute_ppn_gamma` / `compute_g00_trace_ratio` — not a physics failure.
4. If D3 median drops below `v4_D3_median × 0.95`, this must be reported as a regression
   and investigated before claiming v5 as an improvement.
5. No post-hoc gate edits after first run.
6. The `alpha` parameter is fixed at 1.0 for the primary run. Variations in alpha are
   exploratory and do not constitute pre-registered tests.

---

## Script

`scripts/run_qng_metric_hardening_v5.py`

```bash
python scripts/run_qng_metric_hardening_v5.py \
    --dataset-id DS-002 \
    --scales "s0,1.25s0,1.5s0" \
    --samples 72 \
    --seed 3401 \
    --alpha 1.0 \
    --out-dir 05_validation/evidence/artifacts/qng-metric-hardening-v5
```

---

## Expected Artifacts

```
05_validation/evidence/artifacts/qng-metric-hardening-v5/
├── metric_checks.csv         # all gate results (G0, G1, G2, D1-D4, FINAL)
├── eigs.csv                  # per-anchor eigenvalues + sigma_center + eps
├── drift.csv                 # cross-scale drift
├── align_sigma.csv           # cos_sim raw + shuffled
├── vacuum_gate.csv           # G0 data: cond numbers + low-curv flags + sigma_center
├── ppn_gamma.csv             # G1 data: per-anchor gamma, iso_coeff, sigma_center
├── g00_norm_check.csv        # G2 data: per-anchor trace_ratio, h_00, h_spatial
├── config.json               # run configuration (alpha, gates, normalization)
├── eigs-hist.png
├── drift-distribution.png
├── cos-sim-distribution.png
├── cond-number-hist.png
├── gamma-abs-err-hist.png    # NEW: |gamma-1| distribution
├── g00-trace-ratio-hist.png  # NEW: trace_ratio distribution
├── artifact-hashes.json
└── run-log.txt
```

---

## Comparison Criterion (informational, not a gate)

- D3 median v5 ≥ D3 median v4 × 0.95 (no significant regression in sigma alignment)
- D2 median v5 ≤ D2 median v4 × 1.10 (no significant increase in cross-scale drift)

These are informational only and do not gate the v5 verdict.

---

## Open Items (not blocking this pre-registration)

The following items are deferred to future work:

1. **First-principles derivation of ε from graph dynamics** — three candidate
   approaches are documented in `03_math/derivations/qng-epsilon-graph-derivation-candidates-v1.md`.
2. **3D extension of the pipeline** — G2 currently validates the 2D+1 analog
   (trace_ratio = 2.0). The 3D GR target (3.0) requires a 3D graph.
3. **Observational gamma test** — G1 is currently an internal consistency check.
   A genuine PPN test requires the full GR geodesic pipeline against Solar System
   observational data (Cassini: `|γ-1| < 2.3×10⁻⁵`).
