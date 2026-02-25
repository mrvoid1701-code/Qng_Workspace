# QNG — Physical Interpretation of τ (relaxation time)

**Status:** Hypothesis / theoretical draft
**Date:** 2026-02-25
**Scope:** Units, Pioneer calibration, Mercury constraint, minimal τ(Σ) proposals
**For:** Paper section §3 or supplementary material

---

## 1. What is τ?

In the QNG equation of motion, the full acceleration of an object is:

$$a^i = -g^{ij}\partial_j\Sigma \;-\; \tau\,(v\cdot\nabla)(g^{-1}\nabla\Sigma)$$

The second term captures the **memory of the network**: the lattice takes time τ to relax to the new configuration as an object moves through it. The faster the local field changes along the trajectory, the larger the correction.

### Units

If Σ is a gravitational potential with `[Σ] = m²/s²` (same as −GM/r), then:

| Quantity | Units |
|---|---|
| `∇Σ` | m/s² |
| `v · ∇` | 1/s (directional derivative along motion) |
| `(v·∇)(∇Σ)` | m/s³ |
| `a_lag = τ × (v·∇)(∇Σ)` | m/s² |

Therefore **τ has units of seconds** — it is a physical relaxation time of the discrete network, not a dimensionless parameter.

This is the natural interpretation: τ is how long the graph takes to "update" its metric configuration after an object passes through a region. In a perfectly rigid lattice, τ = 0 and QNG reduces to GR. In a lattice with finite relaxation speed, τ > 0 introduces a dissipative correction.

---

## 2. Explicit form of a_lag in the Solar System

For Σ = −GM/r (Newtonian limit, flat metric):

The Hessian of Σ in Cartesian components is:

$$H_{ij} = \partial_i\partial_j\Sigma = \frac{GM}{r^3}\left(\delta_{ij} - \frac{3x_ix_j}{r^2}\right)$$

For an object with velocity **v**, the lag acceleration is:

$$\mathbf{a}_{lag} = -\tau \cdot \frac{GM}{r^3}\left(\mathbf{v} - 3(\mathbf{v}\cdot\hat{r})\,\hat{r}\right)$$

**Radial component** (for a spacecraft moving at radial velocity v_r):

$$a_{lag,r} = +\frac{2\tau\, v_r\, GM}{r^3} \quad \text{(toward Sun for outgoing object)}$$

**Tangential component** (for circular orbit, v_r = 0, v_θ = v_orb):

$$a_{lag,\theta} = -\frac{\tau\, v_\theta\, GM}{r^3}$$

---

## 3. Calibration from Pioneer anomaly

The Pioneer 10/11 spacecraft showed a constant anomalous acceleration directed toward the Sun of:

$$a_P = (8.74 \pm 1.33) \times 10^{-10} \text{ m/s}^2$$

at distances 20–70 AU, with roughly constant radial velocity v_r ≈ 12 km/s.

Setting `a_lag,r = a_P` at r = 40 AU:

$$\tau_{Pioneer} = \frac{a_P\,r^3}{2\,v_r\,GM_\odot} = \frac{8.74 \times 10^{-10} \times (5.98 \times 10^{12})^3}{2 \times 12000 \times 1.327 \times 10^{20}}$$

$$\boxed{\tau_{Pioneer} \approx 5.9 \times 10^4 \text{ s} \approx \textbf{16 hours}}$$

This is a physically interpretable timescale — comparable to the light travel time across the inner solar system (~8 min × ~120 = order hours), or to characteristic dynamical times of near-Earth orbital mechanics.

---

## 4. The Mercury problem — why τ cannot be constant

For Mercury in a near-circular orbit (v_r ≈ 0, v_θ = 47.9 km/s, r = 0.387 AU):

$$a_{lag,\theta}^{Mercury} = \tau \times \frac{GM_\odot \times v_\theta}{r_{Mercury}^3} \approx 1.92 \times 10^{-3} \text{ m/s}^2$$

This tangential deceleration would cause Mercury to lose orbital energy at a catastrophic rate — the orbit would decay measurably within years. Observational constraints on anomalous tangential accelerations at Mercury are below **10⁻¹² m/s²**, meaning constant τ is excluded by a factor of **10⁹**.

Conclusion: **τ must depend on the gravitational environment**, suppressed strongly near the Sun and the inner planets.

---

## 5. Minimal proposals for τ(Σ)

We seek a function τ(Σ) or τ(∇Σ) with:
- τ → 0 in strong fields (GR limit restored)
- τ significant in weak fields (outer solar system, galactic scale)
- At most 1 free parameter beyond the MOND scale a₀

### Proposal A — Velocity-projection coupling (0 extra parameters)

**Key observation:** An object in a circular orbit never crosses equipotential surfaces — the field strength it experiences is constant (dΣ/dt = 0). The "memory" of the lattice should only be excited when the object traverses changing field strength.

**Modification:** Replace `(v·∇)(g⁻¹∇Σ)` with the projection onto the field-gradient direction:

$$a_{lag} = -\tau_0 \cdot (v \cdot \hat{\nabla}\Sigma) \cdot \frac{\partial}{\partial r}(g^{-1}\nabla\Sigma)$$

where `v · ∇̂Σ = v_r` (radial velocity component).

**Consequences:**
- Circular orbits: v_r = 0 → a_lag = **0 exactly**, regardless of τ₀
- Pioneer-type radial flight: full effect, calibrates τ₀ ≈ 16 hours
- Mercury: zero radial anomaly, zero tangential decay — **constraint satisfied by construction**

**Physical meaning:** The lattice relaxation is driven by the rate at which an object encounters new regions of the stability field. An object orbiting at fixed r stays in equilibrium with the lattice; an escaping object constantly enters new lattice territory.

This requires no extra parameters — it is a structural choice in the coupling form.

### Proposal B — Field-strength suppression (1 parameter: τ₀)

$$\tau = \tau_0 \left(\frac{a_0}{|\nabla\Sigma|}\right)^{3/2}$$

where a₀ = 1.2×10⁻¹⁰ m/s² is the MOND acceleration scale (this appears as a natural field-strength threshold, not as a MOND modification — QNG and MOND are distinct theories).

**Result:** With `|∇Σ| = GM/r²`, the lag acceleration becomes:

$$a_{lag,r} = 2\tau_0\, v_r \cdot \frac{a_0^{3/2}}{\sqrt{GM_\odot}}$$

This is **independent of r** for constant v_r — exactly the constant Pioneer anomaly.

**Calibrating τ₀ from Pioneer:**

$$\tau_0 = \frac{a_P\,\sqrt{GM_\odot}}{2\,v_r\,a_0^{3/2}} \approx 3.2 \times 10^{11} \text{ s} \approx 10{,}000 \text{ years}$$

The large value of τ₀ reflects that in the outer solar system (where a₀/|∇Σ| << 1), τ is strongly suppressed from τ₀ — τ_eff at Pioneer ≈ τ₀ × (3.2×10⁻⁵)^{3/2} ≈ 5.9×10⁴ s = 16 hours, consistent with the direct calibration above.

**Note:** Proposal B alone does not fully suppress the tangential anomaly at Mercury. Proposal A (velocity projection) handles that. The two are independent and complementary.

### Recommended minimal form (combined, 1 parameter τ₀):

$$\boxed{\tau_{eff} = \tau_0 \left(\frac{a_0}{|\nabla\Sigma|}\right)^{3/2} \cdot \frac{|v_r|}{|v|}}$$

- `(a₀/|∇Σ|)^{3/2}`: suppresses effect in strong fields, gives constant anomaly at fixed v_r
- `|v_r|/|v|` = cos(θ): suppresses effect for non-radial orbits, vanishes for circular orbits
- Single free parameter: **τ₀ ≈ 3.2×10¹¹ s**

---

## 6. Connection to τ from T-028 (flyby anomaly)

The τ = 0.002051 fitted in T-028 is a **dimensionless regression coefficient** from the graph model, not a physical time in seconds. The connection requires establishing the lattice scale l₀ (lattice spacing in physical units) and a reference velocity v₀:

$$\tau_{physical} = \tau_{graph} \times \frac{l_0}{v_0}$$

Until l₀ is specified, T-028's τ cannot be directly compared to τ_Pioneer. This is the next required theoretical step: identify the physical length scale of the QNG lattice from first principles or from a separate observational constraint.

**One constraint:** If τ_physical ≈ 16 hours and τ_graph = 0.002051, then `l₀/v₀ ≈ 2.9×10⁷ s`. For v₀ = orbital velocity at flyby altitude (~7.9 km/s), this gives l₀ ≈ 2.3×10¹¹ m ≈ 1.5 AU. This is surprisingly similar to the Earth-Sun distance — which could be physically meaningful (lattice scale comparable to the scale of the system being tested) or coincidental.

This connection should be explored in a dedicated section.

---

## Summary

| Quantity | Value |
|---|---|
| Units of τ | seconds |
| τ (constant, from Pioneer) | ≈ 5.9×10⁴ s ≈ 16 hours |
| τ constant: Mercury problem | Excluded by ×10⁹ |
| Minimal fix #1 | Velocity-projection coupling (0 extra params) |
| Minimal fix #2 | τ ∝ (a₀/\|∇Σ\|)^{3/2} (1 param: τ₀) |
| Combined form | τ₀ × (a₀/\|∇Σ\|)^{3/2} × \|v_r\|/\|v\| |
| τ₀ from Pioneer | ≈ 3.2×10¹¹ s ≈ 10,000 years |
| Connection to T-028 | Requires lattice scale l₀ (open) |

The proposed form makes three testable predictions:
1. Pioneer/Voyager anomaly: constant ≈ 8.74×10⁻¹⁰ m/s² for radially escaping probes ✓
2. Circular orbits (Mercury through Saturn): no radial or tangential lag anomaly ✓
3. Eccentric orbits (comets, highly elliptical probes): intermediate effect, proportional to eccentricity ← **new prediction, not yet tested**
