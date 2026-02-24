# QNG Test — Discrete Curl with Memory Lag (QNG-T-CURL-002)

- Date locked: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Status: LOCKED (pre-run)
- Supersedes: QNG-T-CURL-001 (adds lag, v3 vs v4 comparison, memory signature)

---

## Motivation

QNG-T-CURL-001 confirmed that the acceleration field is exactly curl-free in the **constant-metric, lag-free** regime (machine-precision curl). This is a baseline consistency check.

The theory also predicts a **memory lag term**:

```
a_lag^i = −τ (v^j ∂_j)(g^{ij} ∂_j Σ)
```

This term breaks the pure gradient-flow structure: it introduces a time-derivative correction that is **not** curl-free in general. When the lag term is active, the effective acceleration field acquires a nonzero curl proportional to τ and the velocity-gradient product.

**Therefore:**
- **C1 (static, no lag):** curl_rel ≈ 0 → confirmed gradient flow baseline
- **C2 (with lag term):** curl_rel increases measurably → memory signature
- **C3 (shuffle/rewire vs real graph):** must separate differently for lag vs no-lag

This test can distinguish a pure gradient-flow theory (τ = 0) from a memory theory (τ > 0), using only local chart geometry.

---

## Method

### Setup

Same local chart construction as QNG-T-CURL-001: geodesic tangent chart with 20 local nodes per anchor, quadratic Σ fit, linear acceleration model.

### Lag Term Definition

The discrete lag acceleration at anchor `i` is approximated as:

```
a_lag_x(x,y) ≈ −τ · (v_x · ∂²_xx Σ + v_y · ∂²_xy Σ)
a_lag_y(x,y) ≈ −τ · (v_x · ∂²_xy Σ + v_y · ∂²_yy Σ)
```

where `H_ij = ∂²_ij Σ` is the local Hessian from the quadratic fit, and `v = (v_x, v_y)` is a prescribed velocity direction. Since no real velocities are available in the synthetic graph, we test two synthetic velocity cases:

- **v_iso:** `v = (1, 0) / sqrt(2)` (fixed isotropic direction, same for all anchors)
- **v_grad:** `v ∝ −∇Σ / |∇Σ|` (aligned with acceleration — worst case for lag curl)

The total acceleration with lag is:

```
a_total = a_static + τ_test · a_lag
```

where `τ_test = 1.0` (normalized units, making the lag term order-1).

### Curl Estimator

Same as QNG-T-CURL-001: fit linear model `a_x = A + B·x + C·y`, `a_y = D + E·x + F·y`, curl = E − C.

The relative curl uses `|a_static|` as the denominator (not `|a_total|`) to keep the baseline denominator consistent:

```
curl_rel = |curl(a_total)| / max(|a_static|, ε)
```

### Metrics

| Metric | Formula |
|---|---|
| curl_rel_static | |E−C| / |a_static| for a = a_static only |
| curl_rel_lag_iso | |E−C| / |a_static| for a = a_static + τ_test · a_lag(v_iso) |
| curl_rel_lag_grad | |E−C| / |a_static| for a = a_static + τ_test · a_lag(v_grad) |

### v3 vs v4 Metric Comparison

All three metrics are computed using both:
- **v3 metric:** trace normalization (iso = 0.5)
- **v4 metric:** Frobenius normalization (iso = 1/√2)

This yields 6 distributions total. The expectation is that v3 and v4 produce similar static curl (both near zero) but may differ slightly in the lag curl (due to different metric perturbation structure).

### Negative Controls

- **Rewired graph** (50% edge rewire): should show large curl even for static case
- **Shuffled Σ** (random permutation of Σ labels): should show large curl for both static and lag

---

## Pre-registered Gates

### C1 — Static Baseline (gradient flow confirmed)

| Metric | Pass condition |
|---|---|
| median(curl_rel_static, v4) | < 1e-8 (machine precision) |

### C2 — Memory Signature (lag increases curl)

| Metric | Pass condition |
|---|---|
| median(curl_rel_lag_iso, v4) | > 10 × median(curl_rel_static, v4) |
| median(curl_rel_lag_grad, v4) | > 10 × median(curl_rel_static, v4) |

**Interpretation:** The lag term must produce a detectable curl signal (>10× baseline). This is the "memory signature" gate.

### C3 — Control Separation

| Metric | Pass condition |
|---|---|
| median(curl_rel_static, rewired) | > 10 × median(curl_rel_static, v4) |

**Interpretation:** Rewired graph must produce larger curl than the real graph in the static case.

### C4 — v3/v4 Consistency (informational, not a gate)

| Metric | Expectation |
|---|---|
| |median(curl_static_v3) − median(curl_static_v4)| / max | < 2× |
| |median(curl_lag_v3) − median(curl_lag_v4)| / max | < 2× |

The v3 and v4 metrics should produce qualitatively similar curl patterns (order-of-magnitude consistent), even if the exact values differ.

### Overall Decision

PASS = C1 ∧ C2 ∧ C3

---

## Datasets

DS-002, DS-003, DS-006 (seed 3401, 72 anchors)

---

## Anti-Gaming Policy

1. Gates set before running any curl computation.
2. If C2 fails, this is a negative result: the lag term does not produce measurable curl in synthetic data.
3. τ_test = 1.0 is locked (not tuned post-run).
4. No post-hoc gate edits.

---

## Script

`scripts/run_qng_t_curl_002.py`

---

## Expected Artifacts

```
05_validation/evidence/artifacts/qng-t-curl-002/
├── curl_comparison.csv       # per-anchor: static/lag_iso/lag_grad curl_rel (v3 and v4)
├── curl_controls.csv         # per-anchor: rewired + shuffled curl_rel
├── gate_summary.csv          # C1, C2, C3 results
├── curl-memory-signature.png # histogram: static vs lag distributions
├── config.json
├── artifact-hashes.json
└── run-log.txt
```
