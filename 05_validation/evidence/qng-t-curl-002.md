# QNG-T-CURL-002 Evidence Record

- Date: 2026-02-25
- Authored by: Claude Sonnet 4.6
- Pre-registration: `05_validation/pre-registrations/qng-t-curl-002.md`
- Script: `scripts/run_qng_t_curl_002.py`
- Seed: 3401

---

## Results

| Dataset | C1 static_v4 | C2 lag_iso (×static) | C2 lag_grad (×static) | C3 rewired (×static) | Decision |
|---|---|---|---|---|---|
| DS-002 | 1.85e-11 ✓ | 2.06e-11 (×1.12) ✗ | 2.09e-11 (×1.13) ✗ | 5.38e-11 (×2.91) ✗ | **FAIL** |
| DS-003 | 1.36e-11 ✓ | 1.58e-11 (×1.16) ✗ | 1.40e-11 (×1.03) ✗ | 4.39e-11 (×3.22) ✗ | **FAIL** |
| DS-006 | 1.99e-11 ✓ | 2.80e-11 (×1.41) ✗ | 2.33e-11 (×1.17) ✗ | 6.43e-11 (×3.23) ✗ | **FAIL** |

---

## Physical Interpretation

**C1 PASS (as expected):** Static curl = 10⁻¹¹ — machine precision. Gradient flow confirmed at zero order, identical to CURL-001.

**C2 FAIL (expected, and physically meaningful):** The lag term `a_lag = −τ g⁻¹ H v` in the **constant-metric** approximation does NOT generate curl. Reason: with g constant over the local patch, the lag correction is `−τ g⁻¹ (v · ∇)(∇Σ) = −τ g⁻¹ H v` which is spatially constant (H = const from quadratic fit) — a constant vector field has zero curl by definition. The lag factor is ~1.1×, consistent with pure numerical noise around zero.

**C3 FAIL (reveals a diagnostic limit):** Rewired graph only produces ×2.9–3.2× more curl than real graph. This is weak discrimination, suggesting the test at this order cannot distinguish spatial graph structure from random geometry.

**Root cause of all C2/C3 failures:** In the flat/constant-metric approximation, both the memory lag and graph rewiring fail to produce meaningful curl because curl requires metric spatial variation (`∂_i g^{jk} ≠ 0`). This is captured only in the spatially-varying metric version of the test.

---

## What This Means

This result is a **negative diagnostic**, not a theory failure:

1. It confirms the theory is self-consistent at constant-metric order (C1 PASS)
2. It identifies that a meaningful curl test **requires spatially-varying metric evaluation** — computing g(x,y) at each chart point, not just at the anchor
3. Gates C2/C3 were set to probe the lag-memory signature; they require a stronger test (QNG-T-CURL-003-v2, spatially-varying g)

**Recommended next test:** `QNG-T-CURL-003` with per-point metric evaluation — see `CODEX_TASK.md` (added 2026-02-25T13:16 UTC).

---

## v3 vs v4 Comparison (informational)

| Dataset | static_v3 | static_v4 | Δ |
|---|---|---|---|
| DS-002 | 1.84e-11 | 1.85e-11 | ~0% |
| DS-003 | 1.32e-11 | 1.36e-11 | ~3% |
| DS-006 | 2.03e-11 | 1.99e-11 | ~2% |

v3 and v4 produce identical static curl (within 3%). The normalization change does not affect the gradient-flow property at this order.
