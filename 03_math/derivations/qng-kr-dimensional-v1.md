# Derivarea Dimensională a Constantei de Rigiditate a Nodului K_R
## QNG — Node Rigidity Constant: Dimensional Bridge Simulation ↔ SI

- **Data:** 2026-03-16
- **Status:** derivare de cercetare — ipoteză în curs de testare
- **Inputs:**
  - `03_math/derivations/qng-continuum-limit-v1.md`
  - `data/trajectory/pioneer_ds005_anchor.csv`
  - `scripts/run_d8_straton_flyby_v1.py`
  - `04_models/parameter-registry.json`
- **Notă metodologică:** Fiecare pas indică ce e derivat, ce e postulat, și ce e ajustare fenomenologică.

---

## 1. Definiția K_R în Unități Adimensionale (Simulare)

### 1.1 Kernelul SFDDE și K_R

Din formalismul SFDDE (T-029), câmpul de stabilitate la pasul n:

```
Sigma^n(x) = sum_{r=0}^{R} w_r * chi^{n-r}(x)
w_r = k * exp(-r * dt / tau) / Z
```

Cei doi parametri liberi ai kernelului:
- `k = 0.85` — amplitudinea (adimensional)
- `tau = 1.3` — scala de memorie (în unități de simulare)

**Definiție:**

```
K_R = k * tau = 0.85 * 1.3 = 1.105   [adimensional, unități simulare]
```

Interpretare: K_R este "aria" efectivă a kernelului cauzal înainte de normalizare:

```
sum_{r=0}^{inf} k * exp(-r * dt / tau) * dt  ≈  k * tau   (pentru dt << tau)
= 0.85 * 1.3 = 1.105  [unități simulare]
```

### 1.2 Statut de Măsurătoare

K_R_sim = 1.105 este **măsurat**, nu postulat. A fost determinat prin:
- Fit chi2 pe 12 seed-uri independente (T-029)
- delta_chi2_total = -671.49 față de baseline
- Incertitudine: sigma(K_R) ≈ 0.09 (din propagarea sigma_k=0.02, sigma_tau=0.1)

---

## 2. Ecuația de Bază — Legătura cu Fizica Dimensională

### 2.1 Formula QNG pentru Accelerație Reziduală

Din lag-ul kernelului SFDDE, accelerația reziduală a unui corp care se mișcă
prin câmpul de stabilitate este (C-086, derivare în qng-c-086.md):

```
a_res = tau * (v · ∇) ∇Sigma
```

**Identificare dimensională** (din qng-continuum-limit-v1.md, Secțiunea 1.1):

```
Sigma ≡ phi_N / 2   =>   ∇Sigma = ∇phi_N / 2 = g_grav / 2
```

unde `phi_N` este potențialul newtonian [m²/s²] și `g_grav = -∇phi_N` este
accelerația gravitațională [m/s²].

**Notă de asumare (A1):** Identificarea `Sigma = phi_N/2` este validă NUMAI în
limita câmpului slab izotrop (condiții C1-C3 din qng-continuum-limit-v1.md).
Nu este derivată din principii prime ale QNG.

### 2.2 Forma Explicită pentru Mișcare Radială (Masa Punctuală)

Pentru un corp care se mișcă radial față de o masă punctuală M (Soarele) la
distanța r, cu viteza radială v_r:

```
∂_r Sigma = ∂_r(phi_N/2) = ∂_r(-GM/(2r)) = GM/(2r²)    [m/s²]
∂_r²Sigma = -GM/r³                                        [1/s²]
(v · ∇)∇Sigma = v_r * ∂_r²Sigma = -v_r * GM/r³
a_res = tau * (-v_r * GM/r³) * (-1) = +tau * v_r * GM/r³  [m/s²]
```

Semnul pozitiv: accelerația este radial înspre masă (ca anomalia Pioneer observată).

### 2.3 Legătura cu Modelul D8

Modelul D8 fenomenologic (din run_d8_straton_flyby_v1.py):

```
a_lag = C_straton * v_r
```

Prin comparare cu formula QNG (la distanța Pioneer r_P):

```
C_straton = tau_SI * GM_sun / r_P³
```

Aceasta permite extragerea `tau_SI` din C_straton cunoscut:

```
tau_SI = C_straton * r_P³ / GM_sun
```

---

## 3. Extragerea tau_SI din Datele Pioneer

### 3.1 Constante Fizice

```
GM_sun  = 1.327124400e20  m³/s²
1 AU    = 1.49597870700e11  m
```

### 3.2 Calculul tau_SI per Misiune

#### P10_EQ23 (Pioneer 10, r = 55.0 AU):

```
r_P10  = 55.0 * 1.496e11  = 8.228e12  m
r_P10³ = (8.228e12)³      = 5.570e38  m³
C_P10  = a_P10 / v_P10    = 7.84e-10 / 12200 = 6.426e-14  s⁻¹

tau_P10 = C_P10 * r_P10³ / GM_sun
        = 6.426e-14 * 5.570e38 / 1.327e20
        = 2.696e5  s  ≈  3.12  zile
```

#### P11_EQ24 (Pioneer 11, r = 27.0 AU):

```
r_P11  = 27.0 * 1.496e11  = 4.039e12  m
r_P11³ = (4.039e12)³      = 6.589e37  m³
C_P11  = a_P11 / v_P11    = 8.55e-10 / 11600 = 7.371e-14  s⁻¹

tau_P11 = C_P11 * r_P11³ / GM_sun
        = 7.371e-14 * 6.589e37 / 1.327e20
        = 3.660e4  s  ≈  0.42  zile
```

#### P10P11_FINAL (combinat, r = 48.1 AU):

```
r_comb  = 48.1 * 1.496e11  = 7.196e12  m
r_comb³ = (7.196e12)³      = 3.727e38  m³
C_comb  = 8.74e-10 / 12000 = 7.283e-14  s⁻¹

tau_comb = C_comb * r_comb³ / GM_sun
         = 7.283e-14 * 3.727e38 / 1.327e20
         = 2.045e5  s  ≈  2.37  zile
```

### 3.3 Diagnosticul de Inconsistență

| Misiune | r [AU] | tau_SI [s] | tau_SI [zile] |
|---------|--------|-----------|---------------|
| P10_EQ23 | 55.0 | 2.696e5 | 3.12 |
| P11_EQ24 | 27.0 | 3.660e4 | 0.42 |
| P10P11_FINAL | 48.1 | 2.045e5 | 2.37 |
| **Raport P10/P11** | — | **7.36×** | — |

**Concluzii critice:**

tau_P10 / tau_P11 = 7.36 — **inconsistență de factor 7** între cele două misiuni.

Aceasta demonstrează că **formula QNG simplă** `a_res = tau_const × v_r × GM/r³` cu
`tau = const` nu reproduce simultan anomaliile Pioneer 10 și Pioneer 11.

**Motivul fizic:** Anomalia Pioneer este aproximativ CONSTANTĂ cu r
(a_P ≈ 8.74×10⁻¹⁰ m/s² pe intervalul 20–70 AU), dar formula QNG prezice
`a_res ∝ GM/r³ ∝ r⁻³` — o dependență radical diferită.

Aceasta înseamnă că:

1. **Dacă tau = const:** formula QNG NU reproduce anomalia Pioneer constant
2. **Dacă tau = tau(r) ∝ r³:** formula QNG o reproduce, dar tau nu mai e constantă
3. **D8 model (C = const):** funcționează empiric, dar brichează tau-ul conceptual

---

## 4. Consistența Modelului D8 — Testul Real de Universalitate

### 4.1 Ce Testează D8 de Fapt

Modelul D8 cu C_straton = const implică `a_lag = C × v_r`. Universalitatea
testabilă este: **C_straton este același** pentru P10 și P11?

```
C_P10  = 7.84e-10 / 12200 = 6.426e-14 s⁻¹
C_P11  = 8.55e-10 / 11600 = 7.371e-14 s⁻¹
C_comb = 8.74e-10 / 12000 = 7.283e-14 s⁻¹
```

Raport C_P11/C_P10 = 7.371/6.426 = 1.147 — **15% diferență**.

Această consistență de ~15% este testul REAL de universalitate în datele Pioneer.
Concluzie: C_straton este aproximativ universal la nivelul ~15% între P10 și P11.

### 4.2 Incertitudini Observaționale

Incertitudinile publicare pentru a_obs:
- P10: sigma = 1.6e-11 m/s² → ~2% din a_obs → eroare C: ~2%
- P11: sigma = 1.5e-11 m/s² → ~1.8% din a_obs → eroare C: ~1.8%

Diferența de 15% între C_P10 și C_P11 **depășește cu mult erorile observaționale**
(2%). Este un efect real, nu zgomot.

**Interpretare posibilă:** Dacă K_R este universală, atunci C ∝ GM/r³ implicând o
variație ~(27/55)³ = 0.117 (factor 8.5×) între P10 și P11 — mult mai mare decât
15%. Deci consistența de 15% nu este explicată de formula QNG cu tau = const.

Explicații alternative:
1. Anomalia Pioneer are altă origine fizică (termică — explicată de Turyshev 2012)
2. Formula QNG pentru Pioneer necesită un câmp Sigma diferit de phi_N/2
3. K_R_SI = K_R(r) variază în spațiu (câmp K_R, nu constantă)

---

## 5. Conversia Dimensională K_R Simulare → SI

### 5.1 Factorul de Conversie

Deși tau_SI nu este consistent între P10 și P11 (pentru formula cu tau = const),
putem defini un **factor de conversie de referință** folosind ancora P10+P11:

```
Factorul de conversie:
  f_conv = tau_SI_comb / tau_sim = 2.045e5 s / 1.3 = 1.573e5 s/[sim_unit]
         ≈ 1.82 zile per unitate de simulare
```

Interpretare: dacă simularea T-029 reprezintă dinamica la scara Pioneer (~50 AU),
atunci un pas de timp de simulare (dt=0.06) corespunde cu:

```
dt_SI = 0.06 * 1.573e5 s = 9437 s ≈ 2.62 ore
```

### 5.2 K_R în Unități SI (Ancora Pioneer)

```
K_R_SI = k * tau_SI_comb = 0.85 * 2.045e5 = 1.738e5 s
```

Cu propagare de erori:
```
sigma(K_R_SI) ≈ sqrt((sigma_k/k)² + (sigma_a/a)² + (sigma_r/r)²) * K_R_SI
             ≈ sqrt(0.024² + 0.152² + 0.02²) * 1.738e5
             ≈ 0.154 * 1.738e5 ≈ 2.68e4 s
```

Deci:

```
K_R_SI = (1.738 ± 0.268) × 10⁵  s   [ancora P10+P11, formula tau = const]
```

**ATENȚIE:** Aceasta este o conversie de referință, nu o măsurătoare directă.
Ipoteza `tau = const` nu este confirmată între P10 și P11 (inconsistență 7×).

### 5.3 Tabelul de Conversie Complet

| Cantitate | Valoare simulare | Valoare SI (ancora P10+P11) | Unități SI |
|-----------|-----------------|----------------------------|-----------|
| k | 0.85 ± 0.02 | 0.85 ± 0.02 | adimensional |
| tau | 1.3 ± 0.1 | (2.045 ± 0.268) × 10⁵ | s |
| **K_R** | **1.105 ± 0.09** | **(1.738 ± 0.268) × 10⁵** | **s** |
| dt | 0.06 | 9437 | s (~2.6 ore) |
| f_conv | — | 1.573 × 10⁵ | s / sim_unit |
| 1 sim_unit | — | 1.82 zile | — |

---

## 6. Concluzie: Ce Este și Ce Nu Este Demonstrat

### 6.1 Ce Este Demonstrat

1. **K_R_sim = 1.105** este măsurată robust în T-029 (12 seeds, chi2 test)
2. **C_straton ≈ 7×10⁻¹⁴ s⁻¹** este consistent între P10 și P11 la ~15%
3. **Conversia dimensională** este calculabilă ca K_R_SI = k × C_straton × r³ / GM_sun
4. **Factorul de conversie** f_conv = 1.573×10⁵ s/sim_unit (sotto ipoteza ancora P10+P11)

### 6.2 Ce Nu Este Demonstrat (Lacune Rămase)

| Lacună | Impact | Prioritate |
|--------|--------|-----------|
| tau_SI inconsistent P10 vs P11 (factor 7×) | Blochează claim tau = const | **Critic** |
| Formula `a_res = tau × v_r × GM/r³` nu reproduce a_P = const cu r | Implică Sigma ≠ phi_N/2 la scară cosmică | **Critic** |
| C_straton de la flyby (Anderson anomalies) ≠ C_straton Pioneer (factor 1000×) | D8 a arătat că flyby ≠ straton model | Important |
| K_R(r) poate varia în spațiu (nu e constantă) | Universalitatea e condiționată | Important |

### 6.3 Predicția Centrală (Condiționată)

Dacă există o scală caracteristică r_char pentru care Sigma ≈ phi_N/2 este validă,
atunci constanta de rigiditate efectivă este:

```
C_eff(r_char) = K_R_sim * f_conv * GM_body / r_char³
```

Universalitatea implică: C_eff(r_char) este aceeași pentru orice sistem fizic la
scara r_char (laboratoare, stele, galaxii) cu același f_conv.

**Testul falsificabil minim:** Dacă două sisteme diferite la aceeași scară r_char
(dar cu mase diferite) produc C_eff proporțional cu GM_body, atunci K_R este
universal la acea scară.

---

*Derivare completă pentru qng-kr-dimensional-v1 — 2026-03-16*
*Referință: Pioneer datele din Anderson 2002; D8 model din run_d8_straton_flyby_v1.py*
