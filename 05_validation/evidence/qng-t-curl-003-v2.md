# QNG-T-CURL-003-v2 — Evidence: Spatially-Varying Metric Curl Test

**Status:** ✅ ALL PASS (C1 ∧ C2 ∧ C3)
**Run date:** 2026-02-25
**Script:** `scripts/run_qng_t_curl_003_v2.py`
**Pre-registration:** `05_validation/pre-registrations/qng-t-curl-003-v2.md`
**Datasets:** DS-002, DS-003, DS-006

---

## Results

| Dataset | C1 static curl | C2 lag factor | C3 rewire factor | Decision |
|---|---|---|---|---|
| DS-002 | 1.07×10⁻¹⁰ ✅ | 6.28×10⁹ × ✅ | 1.83×10¹¹ × ✅ | **PASS** |
| DS-003 | 2.42×10⁻¹⁰ ✅ | 4.56×10⁹ × ✅ | 5.84×10¹⁰ × ✅ | **PASS** |
| DS-006 | 8.01×10⁻¹¹ ✅ | 5.60×10⁹ × ✅ | 1.18×10¹¹ × ✅ | **PASS** |

**Gate thresholds (locked in prereg before run):**
- C1: `median(curl_rel_static) < 1e-8`
- C2: `lag_factor > 10×` (observed: ~4–6 billion×)
- C3: `rewire_factor > 10×` (observed: ~58–183 billion×)

---

## Physical Interpretation

### C1 — Static curl near zero (gradient flow baseline)
The static acceleration `a_static(x,y) = −g_anchor⁻¹ · ∇Σ(x,y)` uses a **constant metric**
(evaluated at the anchor) with spatially-varying gradient from the quadratic fit.
The result (~1e-10) confirms the gradient flow structure is intact — the acceleration
field is approximately curl-free at the constant-metric level, consistent with
`a = −∂Σ/∂q` at leading order.

### C2 — Lag term produces massive non-zero curl
The lag acceleration `a_lag(x_k) = −τ · g⁻¹(x_k) · H(x_k) · v` is computed with
**per-point metric evaluation**: at each chart node `(x_k, y_k)`, a local sub-quadratic
fit (n_sub=10 nearest nodes) estimates `H(x_k, y_k)`, from which `g(x_k, y_k)` is
computed via `metric_from_sigma_hessian_v4`.

The key physics: when `g⁻¹(x)` and `H(x)` both vary with position, the product
`g⁻¹(x) · H(x)` is generally a position-dependent operator, making `a_lag(x)` a
non-conservative vector field → `curl(a_lag) ≠ 0`.

This confirms the **memory signature** prediction: the τ-lag term introduces
curl into the acceleration field proportional to the spatial variation of the metric.

### C3 — Rewired control: different curl distribution
Shuffling sigma values (randomising the field while preserving magnitudes) produces
a factor ~10¹¹× relative to the static baseline. The rewired curl is even larger than
the real-physics curl because random sigma shuffling creates wildly incoherent local
Hessians, producing maximal curl signal. This confirms the test is sensitive to the
spatial structure of the Sigma field.

---

## Why CURL-002 Failed (C2/C3) — Resolved

CURL-002 used the **constant-metric approximation**: `g = g(anchor)` for all chart
nodes. This made `a_lag = −τ g_anchor⁻¹ · H_anchor · v` a constant vector across
the chart, with zero curl by construction.

CURL-003-v2 fixes this by evaluating `g(x_k)` and `H(x_k)` **per chart point**,
revealing the non-trivial curl that was hidden in the constant-metric approximation.

The static curl (C1) remains near-zero because the isotropic blending in v4 metric
(keep=0.4, iso=1/√2) keeps `g` close to scalar × I, which is nearly curl-free for
the static term. The lag term breaks this symmetry by coupling the varying off-diagonal
structure to the velocity `v`.

---

## Artifacts

```
05_validation/evidence/artifacts/qng-t-curl-003-v2-ds002/
  ├── gate_summary.csv
  ├── curl_rel_values.csv   (per-anchor: static/lag_iso/lag_grad/rewired)
  ├── config.json
  ├── run-log.txt
  └── artifact-hashes.json
(same for ds003, ds006)
```

---

## Parameters

| Parameter | Value |
|---|---|
| Seed | 20260225 |
| Anchors per dataset | 72 |
| Local chart nodes (local_m) | 20 |
| Sub-chart nodes for H(x_k) (n_sub) | 10 |
| τ_test | 1.0 |
| v_iso | (1/√2, 1/√2) |
| anisotropy_keep | 0.4 |
| Rewire noise fraction | ±30% |

---

## Next Steps

- T-SIG-001/002: Numerical Poisson solver with iterative metric-field consistency
- T-SIG-004: Post-Newtonian force correction analytic derivation
- Sensitivity scan with v4 metric (TASKS.md items 77–81)
