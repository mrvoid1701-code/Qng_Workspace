# QNG-T-CURL-001 Evidence Record

- Date: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Pre-registration: `05_validation/pre-registrations/qng-t-curl-001.md`
- Script: `scripts/run_qng_t_curl_001.py`
- Seed: 3401

---

## Results

| Dataset | C1 median | C1 p90 | C2 rewired_med | Decision |
|---|---|---|---|---|
| DS-002 | 1.85e-11 | 6.96e-11 | 5.38e-11 | **PASS** |
| DS-003 | 1.36e-11 | 5.09e-11 | 4.39e-11 | **PASS** |
| DS-006 | 1.99e-11 | 6.01e-11 | 6.43e-11 | **PASS** |

All values are well below the C1 threshold (< 0.10). The rewired graph median is consistently > 1.5× the real graph median (C2 PASS).

---

## Physical Interpretation

The curl values are ~10⁻¹¹ — essentially machine precision. This confirms:

**In the constant-metric (flat) approximation**, the acceleration field `a = −g⁻¹ ∇Σ` with constant `g` is **exactly curl-free**. This is mathematically guaranteed because `a` is a linear transformation of `grad(Σ)`, and the curl of a matrix-times-gradient is zero when the matrix is constant. The test reduces to a numerical sanity check at this order.

**What this means for the theory:**
- The zeroth-order (constant metric) version of the acceleration law is self-consistent: acceleration is a gradient flow.
- The test does NOT yet probe metric spatial variation (which is the source of non-trivial curl in real spacetime). This requires a spatially-varying metric curl test (future: QNG-T-CURL-002).

**Important caveat:** The C2 negative control (rewired graph) also shows very small curl (5–6e-11), only 3–5× larger than the real graph. The separation is weak, reflecting that in the constant-metric approximation, even random acceleration fields can be near-curl-free if the local linear fit has high R². This further supports that the current test is a consistency check, not a strong discriminator.

---

## Status

- QNG-T-CURL-001: **PASS** (constant-metric regime — consistency confirmed)
- QNG-T-CURL-002 (spatially-varying metric, stronger test): **open / future work**

---

## Artifacts

```
05_validation/evidence/artifacts/qng-t-curl-001/
├── curl_results.csv
├── curl_rewired.csv
├── gate_summary.csv
├── config.json
├── curl-distribution.png
├── artifact-hashes.json
└── run-log.txt
```
