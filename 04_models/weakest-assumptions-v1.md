# QNG — Weakest Assumptions Analysis v1

Date: 2026-02-22
Authored by: Claude Sonnet 4.6
Purpose: Satisfy TASKS.md item "Identify weakest assumptions."

This document ranks the core theoretical assumptions of QNG by how well they are supported — from most fragile to most robust.

---

## Ranking: Most Fragile → Most Robust

### 1. WEAKEST — `chi_i = m_i / c` (mass-to-chi mapping)

**Assumption:** The memory coupling parameter chi is proportional to node mass divided by a characteristic speed c.

**Why fragile:**
- This is an ansatz, not derived from first principles.
- The choice of `c` (speed of light? local propagation speed?) is not uniquely fixed by the theory.
- STRATON-002 just returned FAIL (2026-02-22): alpha CV=1.607, LOO=1/13. Mass-scaling is statistically unsupported in the current flyby dataset.
- If chi does not scale with mass, the entire chi-necessity argument (QNG-C-014, QNG-C-029) weakens significantly.

**Current evidence:** FAIL (STRATON-001, STRATON-002). No positive test of mass-dependence to date.

**What would harden it:** a PASS on a richer flyby dataset with diverse masses and low-uncertainty residuals.

---

### 2. FRAGILE — Multiplicative stability closure

**Assumption:** `Sigma_i = clip(Sigma_chi * Sigma_struct * Sigma_temp * Sigma_phi, 0, 1)`

**Why fragile:**
- The multiplicative form is chosen for mathematical convenience (each component independently gates existence), not derived.
- Any additive, weighted, or nonlinear alternative closure could produce qualitatively different node distributions.
- No test directly falsifies multiplicative vs additive closure given the current pipeline.
- The volume rules (V-B) depend on Sigma thresholds that interact with this form.

**Current evidence:** closure gates pass (T-V-01 to T-V-04), but these tests do not distinguish multiplicative from alternative forms.

**What would harden it:** an ablation test comparing multiplicative vs additive closure on the same dataset with the same gates (see TASKS.md P6 ablation items).

---

### 3. FRAGILE — Single global `tau` (universality assumption)

**Assumption:** tau is a universal constant across all missions/domains (trajectory, timing, lensing).

**Why fragile:**
- QNG-T-F02 (cross-mission tau consistency) passes, but only on classic flyby subset with published residuals.
- JUNO, BEPICOLOMBO, SOLAR_ORBITER holdout rows used placeholder delta_v values — not confirmed.
- TAUMAP-001 passes intra-mission stability, but cross-domain (trajectory vs lensing vs timing) universality is untested.
- If tau is domain-dependent, claims QNG-C-060, QNG-C-082, QNG-C-086 decouple and must be defended independently.

**Current evidence:** pass within trajectory domain (classic subset); cross-domain universality not yet tested.

**What would harden it:** QNG-T-SYS01 (global solar system tau fit, listed in TASKS.md Priority A).

---

### 4. MODERATE — Memory kernel form `K(t-t')`

**Assumption:** The memory integral uses a specific kernel shape (exponential decay assumed in most tests).

**Why moderate:**
- The kernel shape is not derived; it is chosen for tractability.
- UNIFY-001 passes a joint fit across lensing + rotation, but with a fixed kernel family.
- A different kernel (power law, oscillatory) could produce different cross-domain behavior.
- HYST-001 tests hysteresis qualitatively but does not constrain the kernel shape quantitatively.

**Current evidence:** pass on pipeline tests with fixed kernel family. Shape not constrained by data.

**What would harden it:** a kernel shape comparison test with BIC selection (similar to STRATON structure).

---

### 5. MODERATE — Volume rule V-B (expansive birth/death)

**Assumption:** Node birth occurs when `Sigma_i >= Sigma_birth` and local coherence passes; node volume grows via beta_plus/beta_minus update.

**Why moderate:**
- V-B was selected over V-A and V-C by gate outcomes in the volume rules test, but all three rules passed some gates.
- The selection was made on a single dataset (DS-002). Cross-dataset stability of V-B selection is not tested.
- The integers `beta_plus`, `beta_minus` are per-dataset free parameters — no physical derivation.

**Current evidence:** V-B selected and locked for v1. No cross-dataset comparison of rule selection yet.

**What would harden it:** running volume rule comparison on DS-003/DS-006 and verifying V-B remains preferred.

---

### 6. ROBUST — Emergent metric from Hessian(Sigma)

**Assumption:** The effective metric is the SPD projection of `-Hessian(Sigma_s)` with conformal gauge normalization.

**Why relatively robust:**
- QNG-T-METRIC-003 passes D1-D4 on DS-002, DS-003, DS-006 with unchanged gates.
- Anti-leak controls (QNG-T-METRIC-004) confirm the signal is not a graph-structure shortcut.
- GR bridge (QNG-T-METRIC-005) shows metric is compatible with GR limit.
- This is the best-tested component of the theory.

**Current evidence:** pass (pipeline level, 3 datasets, anti-leak, GR bridge).

**Remaining gap:** validated on pipeline/synthetic data only; not yet tested on real spacetime data.

---

## Summary Table

| Assumption | Fragility | Current Status | Key Risk |
|---|---|---|---|
| chi = m/c (mass scaling) | ⚠️ Weakest | FAIL (STRATON-002) | chi has no empirical mass dependence found |
| Multiplicative Sigma closure | ⚠️ Fragile | No discriminating test | Alternative closures not tested |
| Global tau universality | ⚠️ Fragile | Pass (trajectory only) | Cross-domain universality untested |
| Memory kernel form | 🔶 Moderate | Pass (fixed kernel) | Kernel shape unconstrained |
| Volume rule V-B | 🔶 Moderate | Pass (DS-002 only) | Cross-dataset rule preference untested |
| Metric = Hessian(Sigma) | ✅ Most robust | Pass (3 datasets, anti-leak, GR bridge) | Pipeline only, no real data |
