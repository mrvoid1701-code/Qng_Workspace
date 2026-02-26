# QNG-STRATON-PRED-001 — Pre-Registered Predictions (v1)

**Date:** 2026-02-26
**Theory document:** `03_math/derivations/qng-straton-interpretation-v2.md`
**Anti-tuning policy:** If any gate fails, a new pre-registration is required.
No thresholds or formulas may be edited post hoc.

---

## Locked inputs

| Parameter | Value | Source |
|-----------|-------|--------|
| τ_graph | 0.002051 | T-028 trajectory fit (metric v4) |
| α | 3/2 | Fixed by constant-anomaly requirement |
| C | 6.992 × 10⁻¹⁴ s⁻¹ | = a_P / v_{r,Pioneer10} |
| l₀,1AU | 0.862 AU | = C × (1 AU)³ × c / (2 τ_graph GM☉) |
| VPC | postulate | Velocity-projection coupling (v_r only) |

## Prediction formula

For any radially escaping probe with heliocentric radial velocity v_r:

    a_anomaly = C × v_r = 6.992 × 10⁻¹⁴ × v_r   [m/s²]

directed toward the Sun.

---

## Gate P1 — Cross-probe velocity scaling

**Prediction:** The anomalous acceleration for Voyager 1 (v_r ≈ 17.0 km/s)
is (36 ± 10)% larger than for Pioneer 10 (v_r = 12.5 km/s).

**Specific values:**

| Probe | v_r (km/s) | Predicted a (m/s²) |
|-------|:----------:|:-------------------:|
| Pioneer 10 | 12.5 | 8.74 × 10⁻¹⁰ (calibration) |
| Pioneer 11 | 11.6 | 8.11 × 10⁻¹⁰ |
| Voyager 1 | 17.0 | 1.19 × 10⁻⁹ |
| Voyager 2 | 15.4 | 1.08 × 10⁻⁹ |
| New Horizons | 14.5 | 1.01 × 10⁻⁹ |

**Gate criterion:** If published tracking-residual analyses exist for any of
Voyager 1/2 or New Horizons, the ratio a_measured / a_predicted must fall
within 0.3–3.0 (order-of-magnitude consistency). A ratio outside this range
falsifies the model.

**Note:** The thermal recoil explanation predicts probe-specific anomalies
depending on RTG geometry, NOT proportional to v_r. The v_r scaling is the
primary discriminant.

---

## Gate P2 — Distance independence

**Prediction:** For a single probe, the anomaly does not vary with heliocentric
distance (beyond measurement noise).

**Gate criterion:** If anomaly measurements exist at two or more distances for
the same probe, the ratio a(r₁)/a(r₂) must be consistent with 1.0 within
measurement uncertainty. A systematic 1/r³ trend (as would follow from
constant t_s) falsifies Scenario B and favors re-examining α.

---

## Gate P3 — Bound-orbit null result

**Prediction:** No secular anomalous acceleration for any planet or satellite
in a near-circular orbit.

**Gate criterion:** Published planetary ephemeris residuals must be consistent
with zero anomalous radial acceleration to within published error bars.
A detection of secular radial drift > 10⁻¹² m/s² for any inner planet
falsifies VPC.

---

## Distinguishability from thermal recoil

| Observable | QNG straton prediction | Thermal recoil prediction |
|------------|----------------------|--------------------------|
| v_r dependence | a ∝ v_r (linear) | No systematic v_r scaling |
| Time dependence | Constant (v_r const.) | Decreases with RTG decay |
| Spacecraft dependence | Same C for all probes | Geometry-specific |
| Distance dependence | None (by construction) | None (RTG independent of r) |

The strongest discriminant is the **v_r scaling**: QNG predicts Voyager 1
anomaly is 36% larger than Pioneer 10; thermal recoil predicts no such
relationship.

---

## What is NOT predicted

- The absolute value of l₀,1AU (calibrated, not derived)
- The curl signature (CURL tests are inconclusive)
- Behavior in strong-field regime (black holes, neutron stars)
- Quantum-scale lattice properties
