# QNG Metric Lock — v4 (Frobenius Normalization)

- Date: 2026-02-24
- Authored by: Claude Sonnet 4.6
- Supersedes: `01_notes/metric/metric-lock-v3.md`
- Status: LOCKED (effective from this document)

---

## Motivation

**v3 vacuum singularity analysis** (`03_math/derivations/qng-continuum-limit-v1.md`) identified a theoretical weakness in trace normalization: when the Sigma field is harmonic (∇²Σ ≈ 0) or nearly flat, the trace of the raw Hessian approaches zero, making the trace normalization floor `max(tr, 1e-12)` dominate and producing a numerically arbitrary metric. In particular:

- At saddle points: λ₁ = −λ₂, so tr(H) = 0 exactly.
- In flat regions: both eigenvalues → 0, and the trace floor 1e-12 is hit.
- Condition number κ(g) = λmax/λmin is unbounded under trace normalization in these regimes.

**Frobenius normalization** resolves this: the Frobenius norm is zero only when ALL matrix entries are zero (truly degenerate Hessian), which is a geometrically meaningful endpoint. It treats all tensor components equally, does not privilege the diagonal, and is invariant under orthogonal frame rotations.

---

## v4 Normalization Rule (LOCKED)

### Step 1 — SPD Projection (unchanged from v3)

Compute eigenvalues of `A = −Hess(Σ)`. Project to SPD:

```
μ₁ = max(|λ₁|, floor)
μ₂ = max(|λ₂|, floor)
g_ij = μ₁ (q₁)ᵢ(q₁)ⱼ + μ₂ (q₂)ᵢ(q₂)ⱼ
```

where `floor = 1e-6`, `q₁, q₂` are the unit eigenvectors.

### Step 2 — Frobenius Normalization (NEW in v4; replaces trace normalization)

```
frob = sqrt(g₁₁² + 2·g₁₂² + g₂₂²)
denom = max(frob, ε_frob)       # ε_frob = 1e-9
g₁₁ /= denom
g₁₂ /= denom
g₂₂ /= denom
```

After this step, the metric satisfies `‖g‖_F = 1` (except in fully degenerate regions where the floor applies).

**Comparison with trace normalization:**

| Property | v3 (trace) | v4 (Frobenius) |
|---|---|---|
| Normalization invariant | trace = 1 | Frobenius norm = 1 |
| Vacuum saddle-point behavior | trace → 0, floor hits | frob ≥ √2·floor, more stable |
| Off-diagonal sensitivity | Low (trace ignores g₁₂) | Equal (Frobenius includes 2g₁₂²) |
| Isotropy of normalization | Diagonal-privileged | Rotationally invariant |
| Anisotropy of result | Preserved via shrinkage | Preserved via shrinkage |

### Step 3 — Anisotropy Shrinkage (preserved from v3, adjusted target)

After Frobenius normalization, blend toward the isotropic matrix with Frobenius norm = 1:

```
iso = 1/sqrt(2) ≈ 0.7071   # isotropic: g₁₁ = g₂₂ = iso, g₁₂ = 0 → frob = 1
k = 0.4                     # anisotropy_keep (unchanged from v3)

g₁₁ = k·g₁₁ + (1−k)·iso
g₂₂ = k·g₂₂ + (1−k)·iso
g₁₂ = k·g₁₂
```

**Note:** The isotropic target changes from `iso = 0.5` (v3 trace convention) to `iso = 1/sqrt(2)` (v4 Frobenius convention) to maintain a consistent normalization invariant after shrinkage.

---

## New Gate: G0 — Vacuum Stability Gate

**Purpose:** Detect and gate low-curvature (near-vacuum) regions where metric quality degrades.

**Definition of low-curvature:** A local chart is "low-curvature" if the raw Frobenius norm of the Hessian before SPD projection satisfies:

```
frob_raw_hessian < low_curv_eps
```

where `low_curv_eps = 0.05` (in normalized graph units after s0 smoothing).

**G0 sub-gates:**

| Sub-gate | Condition | Threshold |
|---|---|---|
| G0a | No NaN or Inf in g₁₁, g₁₂, g₂₂ at any anchor | 0 NaN/Inf |
| G0b | Condition number κ(g) = λmax/λmin, global max | < 1000 |
| G0c | Condition number in low-curvature subset | < 200 |

**Gate G0 PASS:** All three sub-gates pass.

---

## Locked Parameters

| Parameter | v3 Value | v4 Value | Change? |
|---|---|---|---|
| SPD floor | 1e-6 | 1e-6 | No |
| Normalization type | trace | Frobenius | YES |
| Normalization floor | 1e-12 (trace) | 1e-9 (frob) | Adjusted |
| Isotropic target | 0.5 | 1/sqrt(2) | Adjusted |
| Anisotropy keep (k) | 0.4 | 0.4 | No |
| G0 gate | None | Added | New |
| D1–D4 gate thresholds | Unchanged | Unchanged | No |

---

## Backward Compatibility

- **D1–D4 gates are unchanged.** The v4 script re-runs the same protocol as v3 but with Frobenius normalization.
- If v4 passes D1–D4 with results comparable to v3, this confirms that the normalization change is a stability improvement without altering the physical signal.
- If D3 degrades significantly (cos_sim drops), this would indicate the Frobenius normalization changes the directional structure — which would require investigation.

---

## Version History

| Version | Key change |
|---|---|
| v1 | Raw Hessian, no normalization |
| v2 | SPD projection + trace norm (proto) |
| v3 | Unit-trace conformal gauge + anisotropy shrinkage (locked) |
| v4 (this) | Frobenius normalization + G0 vacuum gate (locked) |
