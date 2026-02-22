# Core v1 — Fixed vs Free Parameter Contract

Date: 2026-02-22
Authored by: Claude Sonnet 4.6
Scope: explicit declaration of which parameters are fixed (gates/thresholds/rules) and which are free (scanned within declared ranges) for Core Closure v1.

This document satisfies TASKS.md P6: "Write explicit `fixed vs free` parameter contract for Core v1."

---

## 1) Fixed Parameters (Locked — Cannot Be Tuned Post-Hoc)

These values are frozen for v1. Changing any of them requires opening `core-closure-v2.md` and a new pre-registration.

| Parameter | Value | Where Used | Source |
|---|---|---|---|
| Volume rule | V-B (expansive) | birth/death/update | `01_notes/core-closure-v1.md §3` |
| Chi interpretation | Option A (memory coupling) | `tau_i = alpha_tau * chi_i` | `01_notes/core-closure-v1.md §4` |
| Stability closure | multiplicative | `Sigma = clip(product of components, 0, 1)` | `01_notes/core-closure-v1.md §5` |
| Existence gate threshold | `Sigma_min` (declared per test) | node removal | frozen at test prereg time |
| Birth gate threshold | `Sigma_birth` (declared per test) | node creation | frozen at test prereg time |
| Metric estimator method | SPD projection of `-Hessian(Sigma_s)` | metric hardening | `qng-metric-hardening-v3.md` |
| Conformal gauge | unit-trace normalization | metric hardening | `qng-metric-hardening-v3.md` |
| Anisotropy shrinkage | `k = 0.4` | metric hardening | `qng-metric-hardening-v3.md` |
| Gate D1 epsilon | `eps = 1e-8` | SPD check | `qng-metric-hardening-v3.md` |
| Gate D2 thresholds | `median <= 0.10`, `p90 <= 0.25` | coarse-grain stability | `qng-metric-hardening-v3.md` |
| Gate D3 thresholds | `median cos_sim >= 0.90`, `p10 >= 0.70` | Sigma compatibility | `qng-metric-hardening-v3.md` |
| Gate D4 threshold | `median cos_sim_shuffled < 0.55` | negative control | `qng-metric-hardening-v3.md` |
| Volume integer constraint | `k_i >= 1` for active nodes | volume update | `01_notes/core-closure-v1.md §3` |
| Global volume conservation | NOT conserved in v1 (`dV_tot/dt >= 0`) | expansion regime | `01_notes/core-closure-v1.md §3` |

---

## 2) Free Parameters (Scanned — Allowed to Vary Within Declared Ranges)

These parameters are not fixed to a single value. They are scanned or fit within declared ranges. The ranges are fixed; only the best value within the range is selected.

| Parameter | Declared Range | Selection Method | Test Where Used |
|---|---|---|---|
| Scale `s` | `{s0, 1.25s0, 1.5s0}` | all three evaluated | metric hardening v3 |
| Anchor samples | top-Sigma + stratified random, `n=72` | fixed count, random seed locked | metric hardening v3 |
| `Sigma_grow` | defined per dataset | declared in test prereg | volume rule V-B |
| `Sigma_shrink` | defined per dataset | declared in test prereg | volume rule V-B |
| `beta_plus` | defined per dataset | declared in test prereg | volume rule V-B |
| `beta_minus` | defined per dataset | declared in test prereg | volume rule V-B |
| `alpha_tau` | fit from trajectory/timing tests | inferred from data, not hand-tuned | chi interpretation A |
| `tau` (per mission) | inferred from flyby data | best-fit within physical range | trajectory tests |

**Rule:** any free parameter that is fit to data must be declared in the test pre-registration before the run. Post-hoc range adjustment = protocol violation.

---

## 3) Anti-Tuning Policy

- If a gate fails: gates remain unchanged. No threshold adjustment is permitted.
- If a free parameter scan finds no valid value: test result is FAIL, not a reason to expand the range.
- New parameters introduced after v1 lock require `core-closure-v2.md` + new prereg.
- Seed values used in any run are locked at run time and recorded in the run manifest.

---

## 4) What Is Calibration vs Holdout

| Category | Definition |
|---|---|
| **Calibration set** | Data used to select or tune free parameters before gates are applied |
| **Holdout set** | Data not seen during calibration; used only for locked gate evaluation |
| **Locked gate evaluation** | Run with fixed gates, fixed free-parameter values, on holdout data only |

All calibration/holdout splits must be declared in the test pre-registration. Double-dipping (using holdout data to adjust parameters) is a protocol violation.

---

## 5) Relation to Existing Pre-Registrations

This contract is compatible with and subordinate to all existing locked pre-registrations:

- `qng-metric-hardening-v3.md` — fully consistent with Section 1 fixed values
- `qng-metric-anti-leak-v1.md` — anti-leak controls enforce this contract
- `qng-metric-gr-bridge-v1.md` — GR bridge operates on locked v3 artifacts
- `qng-t-straton-002.md` — trajectory test uses separate free parameter (`alpha`) with its own prereg gates

No existing pre-registration is modified by this document.
