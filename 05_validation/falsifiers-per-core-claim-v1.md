# Falsifiers Per Core Claim — v1

Date: 2026-02-22
Authored by: Claude Sonnet 4.6
Purpose: Satisfy TASKS.md item "Update test plan with at least one falsifier per core claim."

Each core claim lists: what would constitute a definitive falsification, and what test/dataset would produce it.

---

## QNG-C-060 — Trajectory lag term (directional residuals)

**Falsifier:** No statistically significant directional lag term (`v · ∇Σ`) detectable in flyby residuals after all non-gravitational corrections (thermal, SRP, maneuvers), with a dataset of at least 10 diverse missions covering a wide mass and geometry range.

**Falsification test:** QNG-T-P02 (Pioneer directional dependence after all non-grav corrections) + QNG-T-F02 with expanded holdout set.

**Hard-fail threshold:** delta_BIC(lag model vs null) > 0 on expanded holdout, with alpha CV > 1.0.

---

## QNG-C-086a — Directional near-perigee signature

**Falsifier:** Directional signature (inbound vs outbound asymmetry near perigee) disappears after orientation/segment/window randomization controls, across at least 5 diverse missions.

**Falsification test:** QNG-T-TRJ-CTRL-001 expanded to more missions + QNG-T-F03 with locked gates on holdout set.

**Hard-fail threshold:** shuffle controls do NOT collapse signal (control delta_BIC remains < -10 after randomization).

---

## QNG-C-086b3 — Amplitude scaling law (C-086b3)

**Falsifier:** Locked holdout gates fail on missions with disjoint geometry from calibration set, with published delta_v residuals (not placeholder values).

**Falsification test:** C-086b3 holdout rerun with real residuals for JUNO_1, BEPICOLOMBO_1, SOLAR_ORBITER_1.

**Status:** currently in FAIL state with placeholder residuals. Real residuals required before verdict.

---

## QNG-C-058 / QNG-C-082 — Lensing memory offset + rotation curve excess

**Falsifier:** Lensing offsets are fully explained by instantaneous baryonic mass distribution (no lag term needed), confirmed across at least 20 cluster pairs including merging and relaxed systems.

**Falsification test:** QNG-T-027 / QNG-T-039 expanded to real cluster lensing maps (Hubble/JWST/Euclid data), with chi=0 model competitive under BIC.

**Hard-fail threshold:** delta_BIC(memory model vs GR+DM) > 0 on real lensing data with n >= 20 clusters.

---

## QNG-C-083 — History dependence in galaxy halos

**Falsifier:** No difference in rotation curve or lensing profile between galaxies with different formation histories after controlling for current mass, environment, and morphology.

**Falsification test:** matched-galaxy cohort study (old isolated vs recently merged, same current mass) with null result on lag-memory term.

**Hard-fail threshold:** history term adds no predictive power (BIC penalizes it) in a sample of at least 50 matched pairs.

---

## QNG-C-014 — chi necessity (mass-lag coupling)

**Falsifier:** Lag amplitude does not scale with spacecraft mass across missions — constant-tau model is preferred over mass-dependent tau under BIC.

**Falsification test:** QNG-T-STRATON-002 (just run: FAIL). Needs to be replicated on a better dataset.

**Status:** currently FAIL — chi mass-scaling not supported. This is the weakest supported claim in the theory.

**Hard-fail threshold:** STRATON-series FAIL on a dataset with ≥ 20 missions with diverse masses and real residuals.

---

## QNG-CORE-METRIC-V3 — Emergent metric from Hessian(Sigma)

**Falsifier:** On real spacetime data (not pipeline/synthetic), the emergent metric fails gate D3 (Sigma alignment collapses) or D4 (negative control does NOT collapse), indicating the metric is a mathematical artifact of the graph construction rather than a physical signal.

**Falsification test:** QNG-T-METRIC-003 equivalent run on real observational data (trajectory residuals mapped to graph nodes, real lensing data as Sigma proxy).

**Hard-fail threshold:** D3 median cos_sim < 0.70 OR D4 shuffled median > 0.55 on real data.

---

## QNG-H-UNIFY — Single tau universality across domains

**Falsifier:** tau inferred from trajectory tests is inconsistent (by more than 3-sigma) with tau inferred from lensing tests and timing tests, after accounting for measurement uncertainties.

**Falsification test:** QNG-T-SYS01 (global solar system tau fit, TASKS.md Priority A) + cross-domain tau comparison.

**Hard-fail threshold:** tau_trajectory / tau_lensing > 10 or < 0.1 with high confidence.

---

## Framework-Level Falsifier (QNG-C-118)

**Any one of the following constitutes a hard framework falsification:**

1. Tau universality collapses across domains (trajectory vs lensing tau differ by > 10x).
2. Mass-scaling STRATON FAIL on a clean dataset with ≥ 20 diverse missions and real residuals.
3. Directional signature disappears after controls in all tested mission datasets.
4. Metric D4 control fails on real observational data (signal does not collapse under label permutation).
5. Lensing offsets are fully explained without lag-memory on a 20+ cluster real dataset.

If any of the above is confirmed robustly, the theory in its current form is falsified.
