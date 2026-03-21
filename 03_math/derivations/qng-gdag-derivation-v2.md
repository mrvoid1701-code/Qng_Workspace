# QNG: Derivarea Formală a Scalei g† din Geometria Rețelei Discrete — v2

**Status:** Derivare revizuită — reducere de la 2 postulate la 1
**Data:** 2026-03-21
**Dependențe upstream:** qng-metric-hardening-v4 (iso_target = 1/√2, LOCKED)
**Supersede:** qng-gdag-derivation-v1.md

---

## Ce s-a schimbat față de v1

**v1** pornea din iso = 1/√2 (postulat fizic: "echilibrare energetică"), din care
algebric rezulta c_v = √2 − 1.

**v2** inversează ordinea: c_v = √2 − 1 se derivă pur geometric din d_NNN/l₀.
iso = 1/√2 devine consecință, nu postulat. Rămâne un singur postulat fizic explicit
(P1), marcat ca atare — nu mai e ascuns în "echilibrare energetică."

**Structura nouă:**

```
[Geometrie pură] d_NNN = √2·l₀         ← Pitagora
     ↓ definiție c_v
[Geometric]      c_v = √2 − 1          ← fără fizică
     ↓ algebră
[Consecință]     iso = 1 − c_v/√2 = 1/√2   ← derivat, nu postulat
     ↓ P1 (marcat explicit)
[Fizic - P1]    g† = (1−c_v)·a₀       ← singurul postulat rămas
     ↓
[Predicție]      g† = (2−√2)·a₀ = 7.029×10⁻¹¹ m/s²
```

**Open question honest:** P1 nu derivă din Lagrangian. Asta ar fi pasul următor
dacă vrem o teorie complet autonomă.

---

## Rezultat

$$\boxed{g^\dagger = (2 - \sqrt{2}) \times a_0 = 0.5858 \times a_0 = 7.029 \times 10^{-11} \; \text{m/s}^2}$$

Eroare față de valoarea fitată pe 175 galaxii SPARC (3391 puncte): **+0.26%**. Nemodificat față de v1.

---

## Pasul 1 — Geometria rețelei cubice: originea lui c_v

Într-o rețea cubică simplă 3D cu pas $l_0$:

- distanța față-față (nearest neighbor): $d_{NN} = l_0$
- distanța diagonală a feței (next-nearest neighbor): $d_{NNN} = \sqrt{l_0^2 + l_0^2} = \sqrt{2}\,l_0$

**Definiție:** Factorul de dezordine straton $c_v$ este excesul relativ al lui $d_{NNN}$
față de $d_{NN}$:

$$c_v \equiv \frac{d_{NNN} - l_0}{l_0} = \frac{\sqrt{2}\,l_0 - l_0}{l_0} = \sqrt{2} - 1$$

Aceasta este o **identitate geometrică pură** (Pitagora). Nu conține nicio ipoteză fizică.

**Valoare numerică:** $c_v = \sqrt{2} - 1 = 0.41421\ldots$

---

## Pasul 2 — iso ca derivat din c_v (nu postulat)

În metrica QNG cu normalizare Frobenius (preregistrată în hardening v4):

$$\|g\|_F^2 = 3a^2 + b^2 = 1, \qquad
\text{iso} = \sqrt{3}\,|a|, \qquad
\text{aniso} = |b|$$

**Legătura cu c_v:** componenta anizotropă a grafului este fracția
din norma totală purtată de dezordinea straton:

$$\text{aniso} = \frac{c_v}{\sqrt{2}} = \frac{\sqrt{2}-1}{\sqrt{2}} = 1 - \frac{1}{\sqrt{2}}$$

Deoarece $\text{iso}^2 + \text{aniso}^2 = 1$:

$$\text{iso}^2 = 1 - \left(1 - \frac{1}{\sqrt{2}}\right)^2
= 1 - 1 + \sqrt{2} - \frac{1}{2} = \frac{1}{2}
\implies \boxed{\text{iso} = \frac{1}{\sqrt{2}}}$$

**Aceasta reproduce valoarea din hardening v4 ca consecință geometrică.**
Nu mai e nevoie de condiția "iso/aniso = 1" (echilibrare energetică) — ea este
automat satisfăcută când c_v este definiția geometrică de mai sus.

**Verificare:**

$$\text{iso} + \frac{c_v}{\sqrt{2}} = \frac{1}{\sqrt{2}} + \frac{\sqrt{2}-1}{\sqrt{2}}
= \frac{1}{\sqrt{2}} + 1 - \frac{1}{\sqrt{2}} = 1 \quad \checkmark$$

$$\text{iso}^2 + \text{aniso}^2 = \frac{1}{2} + \frac{1}{2} = 1 \quad \checkmark$$

---

## Pasul 3 — Metrica QNG cu normalizare Frobenius (nemodificat față de v1)

Din Pasul 2, $\text{iso} = 1/\sqrt{2}$ și $\text{iso} = \sqrt{3}\,|a|$:

$$|a| = \frac{1}{\sqrt{6}}, \qquad
g_{ij}^{\text{iso}} = \frac{1}{\sqrt{6}} \cdot \delta_{ij}$$

---

## Pasul 4 — **[P1]** Cuplajul straton: g† = (1−c_v)·a₀

**Postulat P1 (singurul postulat fizic rămas, nededus din Lagrangian):**

Probabilitatea de ocupație a unui nod straton la accelerație $g_\text{bar}$:

$$P_\text{straton}(r) = \exp\!\left(-\frac{g_\text{bar}(r)}{g^\dagger}\right)$$

Scara de tranziție $g^\dagger$ este proporțională cu fracția de spațiu
**liber** al grafului (neocupat de dezordinea straton):

$$g^\dagger = (1 - c_v) \times a_0 = (2 - \sqrt{2}) \times a_0$$

**De ce P1 nu e derivat:** Legătura $g^\dagger = (1-c_v)\times a_0$ este motivată
fizic (fracție liberă × scara MOND), dar nu rezultă dintr-o ecuație de câmp QNG.
O derivare riguroasă ar porni din acțiunea discretă QNG și ar arăta că scara de
tranziție a supresiei straton este exact $(1-c_v)\times a_0$.

**Că $a_0$ apare ca intrare externă** este o limitare separată — un cadru complet
ar deriva $a_0$ emergent din $\tau_\text{graph}$ și densitatea nodurilor.

---

## Pasul 5 — Rezultat numeric și verificare (nemodificat față de v1)

| Cantitate | Valoare derivată | Valoare fitată SPARC | Eroare |
|-----------|-----------------|---------------------|--------|
| $g^\dagger / a_0$ | $2 - \sqrt{2} = 0.58579$ | $0.58438$ | +0.24% |
| $g^\dagger$ [m/s²] | $7.029 \times 10^{-11}$ | $7.011 \times 10^{-11}$ | +0.26% |

---

## Contabilitatea postulateor

| Postulat | v1 | v2 |
|----------|----|----|
| "Echilibrare energetică iso/aniso = 1" | ✓ (ascuns în geometrie) | ✗ eliminat |
| P1: $g^\dagger = (1-c_v)\times a_0$ | ✓ (implicit în Pasul 4) | ✓ **marcat explicit** |
| Definiție $c_v = d_{NNN}/l_0 - 1$ | implicit | ✓ explicit geometric |

**Reducere: 2 postulate → 1 postulat (P1), marcat onest.**

---

## Lanțul cauzal complet (v2)

```
Rețea cubică 3D (geometrie euclidiană standard)
  ↓ Pitagora: d_NNN = √2·l₀
c_v = √2 − 1 = 0.4142        ← GEOMETRIC, fără fizică
  ↓ algebră: aniso = c_v/√2, iso² + aniso² = 1
iso = 1/√2                    ← CONSECINȚĂ (reproduce hardening v4)
  ↓ [P1: singurul postulat fizic, nededus din Lagrangian]
g† = (1−c_v)·a₀ = (2−√2)·a₀  ← FIZIC (fracție liberă × scara MOND)
  ↓ testare pe 175 galaxii SPARC (N=3391), fără fit suplimentar
Eroare față de fit: +0.26%
```

---

## Open questions (onest documentate)

1. **P1 nu derivă din Lagrangian.** Legătura $g^\dagger = (1-c_v)\times a_0$
   este motivată fizic, dar nu rezultă dintr-o ecuație de câmp. Pasul următor
   spre o teorie complet autonomă.

2. **$a_0$ apare ca intrare externă.** Un cadru complet ar deriva $a_0$ emergent
   din parametrii QNG fundamentali ($\tau_\text{graph}$, densitatea nodurilor).

3. **VPC rămâne postulat.** Necesar pentru consistența cu sistemul solar, dar
   nu este derivat din simetria rețelei discrete.

---

## Verificare numerică independentă

```python
import math

a0  = 1.2e-10   # m/s^2 (Milgrom)
l0  = 1.0       # pas rețea (unități relative)

# Pasul 1: c_v pur geometric
d_NNN = math.sqrt(2) * l0
cv    = (d_NNN - l0) / l0          # = sqrt(2) - 1
print(f"c_v = (d_NNN - l0)/l0 = {cv:.6f}")       # 0.414214

# Pasul 2: iso ca consecință
aniso = cv / math.sqrt(2)          # = 1 - 1/sqrt(2)
iso   = math.sqrt(1 - aniso**2)    # = 1/sqrt(2)
print(f"iso = {iso:.6f}  (= 1/√2 = {1/math.sqrt(2):.6f})")  # 0.707107

# Pasul 4 [P1]: g†
gdag  = (1 - cv) * a0              # = (2 - sqrt(2)) * a0
print(f"g†  = (2−√2)·a₀ = {gdag:.4e} m/s^2")     # 7.029e-11

# Verificări consistență
assert abs(iso**2 + aniso**2 - 1.0) < 1e-12
assert abs(iso - 1/math.sqrt(2)) < 1e-12
assert abs(cv - (math.sqrt(2) - 1)) < 1e-12

print(f"Eroare vs fit SPARC: {(gdag - 7.011e-11)/7.011e-11*100:+.3f}%")  # +0.263%
```
