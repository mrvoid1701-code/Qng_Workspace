# QNG-STRATON-DISCR-001 — Data Discriminator: Thermal vs v_r Regression

**Date:** 2026-02-26
**Theory document:** `03_math/derivations/qng-straton-interpretation-v2.md` (§ 9.2)
**Anti-tuning policy:** Gates locked before any data comparison. No threshold edits.

---

## 1. Objective

Determine whether published tracking-residual data for deep-space probes are
better explained by:

- **H_thermal:** RTG thermal recoil (spacecraft-specific, decaying with RTG power)
- **H_QNG:** Straton lag (universal C × v_r, constant at constant v_r)
- **H_joint:** Both contributing

## 2. Available data assessment (pre-analysis)

### 2.1 Pioneer 10/11

**Usable.** Spin-stabilized, minimal thruster firings, Doppler tracking to
~10⁻¹⁰ m/s² precision. Extended dataset spans 1987–1998 (Pioneer 10) and
1987–1990 (Pioneer 11). Published in Anderson et al. (2002), reanalyzed by
Turyshev et al. (2012).

**Key constraint from literature:** Turyshev et al. (2012) report a temporal
decay rate ~2 × 10⁻¹¹ m/s²/yr, with 10%+ improvement in residuals compared
to constant-acceleration model. The decay half-life is consistent with Pu-238
RTG half-life (87.72 yr).

**Implication for QNG:** If the anomaly genuinely decays with RTG power, this
is **direct tension** with H_QNG, which predicts constant anomaly at constant v_r.
Pioneer's v_r is approximately constant over the data interval, so QNG predicts
a_QNG = const. The observed decay favors H_thermal.

### 2.2 New Horizons

**Partially usable.** Measured non-gravitational acceleration
~1.25 × 10⁻⁹ m/s² sunward (Folkner et al. 2008–era analyses). Thermal model
predicts ~1.15 × 10⁻⁹ m/s² from RTGs mounted close to body. Acceleration is
decreasing over time, consistent with thermal.

QNG prediction for New Horizons: C × v_r = 6.99 × 10⁻¹⁴ × 14,500
= 1.01 × 10⁻⁹ m/s². This is within the measurement envelope, but so is
thermal recoil. **Not discriminating at current precision.**

### 2.3 Voyager 1/2

**Not usable.** Three-axis stabilized, frequent thruster firings for attitude
control. Navigation noise exceeds 10⁻⁹ m/s². Cannot detect Pioneer-scale
anomalies. The QNG cross-probe prediction (Voyager 1 anomaly = 1.19 × 10⁻⁹)
is **untestable with current Voyager data.**

### 2.4 Cassini

**Not usable for this test.** Bound orbit around Saturn during prime mission;
radial velocity oscillates. However, Cassini cruise phase (1997–2004) involved
multiple gravity assists with varying v_r. Thermal effects from RTGs are
complex (three RTGs, asymmetric mounting).

## 3. Joint regression model

For Pioneer 10 extended Doppler data (primary dataset):

$$a_{\text{meas}}(t) = a_{\text{thermal},0} \cdot e^{-\lambda t}
+ C_{\text{QNG}} \cdot v_r(t) + a_{\text{baseline}} + \epsilon(t)$$

where:
- $\lambda = \ln 2 / 87.72\,\text{yr} = 7.90 \times 10^{-3}\,\text{yr}^{-1}$ (RTG decay)
- $v_r(t)$ is the heliocentric radial velocity at time $t$
- $a_{\text{baseline}}$ absorbs systematic biases
- $\epsilon(t)$ is measurement noise

Fit parameters: $(a_{\text{thermal},0},\; C_{\text{QNG}},\; a_{\text{baseline}})$.
$\lambda$ is fixed (known Pu-238 half-life).

## 4. Gates

### Gate D1 — QNG coefficient significance

**Test:** Is $C_{\text{QNG}}$ statistically distinguishable from zero?

- **PASS:** $C_{\text{QNG}} / \sigma_{C} > 2$ (95% CL detection)
- **FAIL:** $C_{\text{QNG}} / \sigma_{C} \leq 2$ (no evidence for v_r term)

### Gate D2 — QNG coefficient value

**Test:** If D1 passes, is $C_{\text{QNG}}$ consistent with the predicted value?

- **PASS:** $|C_{\text{QNG}} - 6.99 \times 10^{-14}| < 3\sigma_C$
- **FAIL:** Detected but wrong value (QNG model wrong in detail)

### Gate D3 — Model comparison

**Test:** Does the joint model (thermal + QNG) improve over thermal-only?

- **PASS:** $\Delta\text{BIC}_{\text{joint vs thermal}} < -6$ (strong evidence for additional term)
- **FAIL:** $\Delta\text{BIC} \geq -6$ (thermal-only sufficient)

### Gate D4 — Temporal decay test (QNG-specific)

**Test:** Does the anomaly show temporal decay inconsistent with constant QNG?

- **PASS (for QNG):** Residuals after subtracting thermal model show no
  significant trend (constant remainder consistent with C × v_r)
- **FAIL (for QNG):** Thermal-only model absorbs all temporal variation,
  leaving residuals consistent with zero

## 5. Pre-analysis assessment: QNG faces headwinds

**Honest statement:** Based on published results (Turyshev et al. 2012), the
Pioneer anomaly data already favor thermal recoil:

1. The anomaly shows temporal decay consistent with RTG half-life.
2. Finite-element thermal modeling reproduces magnitude, direction, and
   temporal behavior.
3. After thermal correction, no statistically significant residual remains.

**This means Gates D1–D3 are likely to FAIL for QNG** if the Turyshev analysis
is correct. The discriminator test is pre-registered honestly: we expect
thermal to dominate, and the QNG term to be consistent with zero.

**However, the test remains scientifically valuable because:**

1. If a small but significant v_r-correlated residual survives thermal
   correction, it would be evidence for an additional physical effect.
2. The test structure is reusable for future missions with better data
   (e.g., a dedicated Pioneer-like probe with modern instrumentation).
3. Null results are informative: D1 FAIL constrains the QNG coupling
   constant to $C < 2\sigma_C$ upper bound.

## 6. Data sources

- Anderson, J. D., et al. (2002). "Study of the anomalous acceleration of
  Pioneer 10 and 11." Phys. Rev. D 65, 082004.
- Turyshev, S. G., et al. (2012). "Support for the thermal origin of the
  Pioneer anomaly." PRL 108, 241101.
- Folkner, W. M. (2010). Planetary ephemeris DE421 and New Horizons
  tracking notes.

## 7. Contingency: what if QNG fails all gates?

If D1–D4 all indicate thermal-only:

- The straton layer is **not falsified** (it predicts a small effect that may be
  below current detection threshold when thermal dominates).
- But it is **unfalsifiable with current data**, which is a weakness.
- The straton prediction becomes a statement about future experiments:
  a purpose-built, spin-stabilized probe with minimal thermal asymmetry
  and high-precision accelerometry would be needed.
- Upper bound on C from Pioneer data becomes a constraint on l₀,1AU.

## 8. What this prereg does NOT claim

- We do NOT claim that QNG will be detected in existing data.
- We do NOT claim thermal recoil is wrong.
- We DO claim that the regression framework is the correct way to look
  for a v_r-correlated signal, and that a null result is informative.
