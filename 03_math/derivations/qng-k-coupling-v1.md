# Derivarea Parametrului k din Cuplajul Straton — v1

**Status:** Investigație deschisă — k rămâne parțial derivat
**Data:** 2026-03-06

---

## Rezumat

Parametrul `k = 0.8556` (fit SPARC) nu este complet derivat teoretic.
Cel mai bun candidat din geometria straton este `k² = (3−√2)/2 = 0.7929`,
adică `k = 0.8904` (eroare +4.1%). Documentul prezintă toate abordările testate.

---

## Candidați derivați

| Formula | k_derivat | Eroare vs 0.8556 | Motivație |
|---------|-----------|-----------------|-----------|
| `(2−√2)^(1/3)` | 0.8367 | −2.2% | **cel mai aproape numeric** |
| `√((3−√2)/2)` | 0.8904 | +4.1% | motivat fizic (corecție 1/2 orbitală) |
| `1/√2 × aniso_corr` | 0.7071 | −17.4% | norma Frobenius radială |
| `√(2/3) × (2−√2)` | 0.4783 | −44.1% | proiecție 3D→2D × fracție straton |

---

## Abordarea 1: Corecție Orbitală (k² = 1 − cv/2)

**Rațiune:**

Pe o orbită circulară galactică ($v_r = 0$, $v_\theta = v_{\text{circ}}$),
termenul T3 acționează prin câmpul straton al discului galactic integrat pe linia
de vedere. Media azimutală a cuplajului produce un factor de reducere față de
cuplajul total 3D.

**Derivare:**

Cuplajul total (3D izotrop): $k_{\text{total}}^2 = 1$

Reducere din fracția straton ocupată: $-c_v$ (stratoni activi nu propagă)

Reducere din media orbitală: media $\langle \cos^2\theta \rangle = 1/2$ pe orbită circulară
(câmpul radial vs direcție orbitală tangențială)

$$k^2 = 1 - c_v \times \frac{1}{2} = 1 - \frac{\sqrt{2}-1}{2} = \frac{3 - \sqrt{2}}{2}$$

$$k = \sqrt{\frac{3 - \sqrt{2}}{2}} = 0.8904 \quad (\text{eroare: } +4.1\%)$$

**Limita acestei derivări:** factorul 1/2 pentru media orbitală e o aproximare
grosieră — media corectă depinde de distribuția radială a masei barionice,
care variază de la galaxie la galaxie.

---

## Abordarea 2: k din Cubic Root (k = (2−√2)^(1/3))

**Rațiune:** Dacă T3 e o funcție de energie pe 3 axe ale rețelei cubice,
cuplajul per axă e $(2-\sqrt{2})$, iar cuplajul total pe orbita 2D e media
geometrică pe 3 axe:

$$k = (2 - \sqrt{2})^{1/3} = 0.8367 \quad (\text{eroare: } -2.2\%)$$

Aceasta e cel mai aproape numeric, dar justificarea fizică e slabă.

---

## Abordarea 3: k din Norma Frobenius a Tensorului de Cuplaj

**Rațiune:** Tensorul de cuplaj QNG are componenta radial efectivă egală cu
norma componentei anizotrope a metricii: $\|C_{rr}\| = \text{aniso} = 1/\sqrt{2}$.

$$k = \frac{1}{\sqrt{2}} = 0.7071 \quad (\text{eroare: } -17.4\%)$$

Prea mic față de fit.

---

## Concluzie

**k nu este derivat complet.** Cel mai bun candidat din teoria straton:

$$\boxed{k \approx (2 - \sqrt{2})^{1/3} = 0.837 \quad \text{sau} \quad k = \sqrt{\frac{3-\sqrt{2}}{2}} = 0.890}$$

cu erori de 2–4% față de fit. Pentru un preprint, k poate fi tratat ca parametru
liber de ordin 1, cu nota că valorile derivate teoretic sunt în acord la 5%.

**Derivarea riguroasă** ar necesita:
1. Calculul explicit al cuplajului T3 din acțiunea QNG discretă (integral de path)
2. Proiecția pe orbita circulară galactică în prezența discului barion real
3. Testul că k_derivat reproduce BFTF (Baryonic Tully-Fisher Factor) corect
