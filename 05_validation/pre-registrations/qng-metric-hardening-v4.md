# QNG Metric Hardening v4 — Pre-registration

- Date locked: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Status: LOCKED (pre-run)
- Supersedes: `qng-metric-hardening-v3.md`
- Method lock reference: `01_notes/metric/metric-lock-v4.md`

---

## Purpose

Validate the v4 metric normalization (Frobenius norm) as a stability improvement over v3 (trace normalization). Primary goal: confirm the new G0 vacuum stability gate passes and that D1–D4 results are consistent with v3.

---

## Pre-registered Protocol

### Datasets (identical to v3)

| Dataset | Role | n nodes | k neighbors | seed |
|---|---|---|---|---|
| DS-002 | Primary | 280 | 8 | 3401 |
| DS-003 | Cross-validation | 240 | 7 | 3401 |
| DS-006 | Replication | 320 | 9 | 3401 |

### Scales

`s0, 1.25s0, 1.5s0` (same as v3)

### Samples

72 anchors (same as v3)

---

## Pre-registered Gates

### G0 — Vacuum Stability Gate (NEW in v4)

| Sub-gate | Metric | Pass condition |
|---|---|---|
| G0a | NaN/Inf count in metric components | = 0 |
| G0b | max condition number κ = λmax/λmin (global) | < 1000 |
| G0c | max κ in low-curvature subset (frob_hessian < 0.05) | < 200 |

**G0 PASS:** G0a ∧ G0b ∧ G0c

### D1 — SPD/Signature Gate (unchanged from v3)

| Metric | Pass condition |
|---|---|
| min_eig_global | ≥ 1e-8 |

### D2 — Coarse-Grain Stability Gate (unchanged from v3)

| Metric | Pass condition |
|---|---|
| median(Δg_frob_rel) | ≤ 0.10 |
| p90(Δg_frob_rel) | ≤ 0.25 |

### D3 — Sigma Compatibility Gate (unchanged from v3)

| Metric | Pass condition |
|---|---|
| median(cos_sim) | ≥ 0.90 |
| p10(cos_sim) | ≥ 0.70 |

### D4 — Negative Control Collapse Gate (unchanged from v3)

| Metric | Pass condition |
|---|---|
| median(cos_sim_shuffled) | < 0.55 |

### Overall Decision

PASS = G0 ∧ D1 ∧ D2 ∧ D3 ∧ D4

---

## Anti-Gaming Policies

1. Gates are set before running any v4 code.
2. If G0 fails, the fix must address the vacuum singularity without changing D1–D4 thresholds.
3. If D3 median drops below 0.90 relative to v3, this must be reported as a regression, not corrected by gate relaxation.
4. Comparison with v3 results is informational only — the v4 gates are evaluated independently.
5. No post-hoc gate edits after first run.

---

## Script

`scripts/run_qng_metric_hardening_v4.py`

---

## Expected Artifacts

```
05_validation/evidence/artifacts/qng-metric-hardening-v4/
├── metric_checks.csv         # gate results
├── eigs.csv                  # per-anchor eigenvalues
├── drift.csv                 # cross-scale drift
├── align_sigma.csv           # cos_sim raw + shuffled
├── vacuum_gate.csv           # G0 data: cond numbers + low-curv flags
├── config.json               # run configuration
├── eigs-hist.png
├── drift-distribution.png
├── cos-sim-distribution.png
├── cond-number-hist.png      # NEW: condition number distribution
├── artifact-hashes.json
└── run-log.txt
```

---

## Comparison Criterion (informational, not a gate)

If v4 passes and v3 also passed, confirm:
- D3 median v4 ≥ D3 median v3 × 0.95 (no significant regression)
- D2 median v4 ≤ D2 median v3 × 1.10 (no significant increase in drift)

These are informational only and do not gate the v4 verdict.
