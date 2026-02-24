# QNG Test — Curl of Acceleration Field (QNG-T-CURL-001)

- Date locked: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Status: LOCKED (pre-run)
- Related claim: QNG-C-093 (acceleration law a = −g^{ij} ∂_j Σ)
- Related derivation: `03_math/derivations/qng-continuum-limit-v1.md` §5

---

## Motivation

The QNG acceleration law is:

```
a^i(x) = −g^{ij}(x) ∂_j Σ(x)
```

If this law holds with a well-defined metric g and scalar field Σ, then the acceleration field is the gradient of a scalar potential (up to metric corrections). In the flat limit (g ≈ g₀ constant), a = −∇Σ is a pure gradient and therefore **curl-free**:

```
curl(a) = ∂_x a_y − ∂_y a_x = 0
```

More precisely: if a^i = −g^{ij} ∂_j Σ and the metric is symmetric but position-dependent, then:

```
∂_x a_y − ∂_y a_x = −(∂_x g^{yj} ∂_j Σ − ∂_y g^{xj} ∂_j Σ)
```

This is nonzero in general (due to metric variation), but should be **small relative to |a|** whenever the metric varies slowly compared to the Sigma gradient scale — which is exactly the assumption underlying the continuum limit (A1 in `qng-discrete-to-continuum-v1.md`).

**Therefore:** A large relative curl magnitude is a direct indicator that the metric is inconsistent, that A1 fails, or that the acceleration law is ill-defined. This test is a cheap but powerful consistency check.

---

## Method

### Curl Estimator

In each local geodesic tangent chart (2D, same as metric hardening), fit a local linear model for the acceleration field components:

```
a_x(x, y) ≈ A + B·x + C·y
a_y(x, y) ≈ D + E·x + F·y
```

via ordinary least squares (OLS) over the local chart nodes (excluding the anchor at origin).

The curl estimate at the anchor is:

```
curl ≡ E − C   (= ∂_x a_y − ∂_y a_x at origin)
```

The magnitude of the acceleration at the origin is estimated as:

```
|a| = sqrt(a_x(0,0)^2 + a_y(0,0)^2) = sqrt(A^2 + D^2)
```

The relative curl is:

```
curl_rel = |curl| / max(|a|, epsilon)
```

where `epsilon = 1e-6` prevents division by zero in flat regions.

### Negative Control

Repeat the same curl estimation on a **graph-rewired** dataset: randomly rewire 50% of edges (preserving node degrees) to destroy the spatial structure, while keeping Sigma values fixed. The rewired graph should produce **large** relative curl (the acceleration field becomes incoherent), confirming the test discriminates physical structure from noise.

---

## Pre-registered Gates

### C1 — Curl Magnitude Gate

| Metric | Pass condition |
|---|---|
| median(curl_rel) | < 0.10 |
| p90(curl_rel) | < 0.30 |

### C2 — Negative Control Separation Gate

| Metric | Pass condition |
|---|---|
| median(curl_rel_rewired) | > median(curl_rel_real) × 1.5 |

**Interpretation:**
- C1 PASS: The acceleration field is nearly curl-free at the median local patch, consistent with the gradient-flow law.
- C2 PASS: The rewired control yields a larger curl than the real graph, confirming the test has discriminative power.

### Overall Decision

PASS = C1 ∧ C2

---

## Datasets

Same as metric hardening: DS-002, DS-003, DS-006 (seed 3401, 72 anchors).

---

## Anti-Gaming Policy

1. Gates set before running any curl estimation code.
2. If C1 fails, this is reported as a violation of the gradient-flow assumption, not corrected by threshold relaxation.
3. The negative control must be run regardless of C1 outcome.
4. No post-hoc gate edits after first run.

---

## Script

`scripts/run_qng_t_curl_001.py`

---

## Expected Artifacts

```
05_validation/evidence/artifacts/qng-t-curl-001/
├── curl_results.csv          # per-anchor: curl, |a|, curl_rel
├── curl_rewired.csv          # per-anchor: curl_rel on rewired graph
├── gate_summary.csv          # C1, C2, overall decision
├── curl-distribution.png     # histogram of curl_rel (real vs control)
├── config.json
├── artifact-hashes.json
└── run-log.txt
```
