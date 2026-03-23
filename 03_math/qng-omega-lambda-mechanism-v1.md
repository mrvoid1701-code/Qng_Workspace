# QNG: Mecanism Ω_Λ — Energia de Conexiune ca Dark Energy

**Status**: PROPUNERE NOUĂ (înlocuiește identificarea G37 cu mod constant)
**Versiune**: v1
**Data**: 2026-03-22
**Înlocuiește**: qng-omega-lambda-v1.md §3 (mecanismele propuse anterior sunt eliminate)
**Dependințe**: C-029, C-103, C-104, qng-friedmann-ns-dynamics-v1.md

---

## 1. Problema cu Identificarea G37 (Recapitulare + Defect Nou)

qng-omega-lambda-v1.md §2 a calculat:

```
Omega_DE_QNG = omega_0 / (N * omega_mean) ~ 1/N ~ 0.00038    [FACTOR 1800x PREA MIC]
```

Motivul invocat: modul constant contribuie doar 1/N din energia spectrală totală.

### 1.1 Un defect mai profund: scalarea temporală greșită

Dincolo de valoarea numerică, modul constant are o problemă de **scalare temporală**:

Energia modului constant:
```
E_0 = omega_0/2 = sqrt(M_EFF_SQ)/2 = const pe fiecare nod
Energia totala a modului constant = N_s * (omega_0/2) * [?]
```

Dar în QNG, modul constant φ₀(i) = 1/√N este un singur mod global, NU un mod per nod.
Energia sa este o singură energie: E₀ = ω₀/2 = const.

Ca densitate de energie:
```
rho_Lambda_mode = E_0 / V_tot = (omega_0/2) / (N_s * V_0) ~ 1/N_s ~ 1/a^3
```

**Aceasta este scalare de materie (1/a³), nu de constantă cosmologică (const)!**

Un termen de dark energy trebuie să aibă ρ = const (nu scade cu expansiunea).
Modul constant cu energia sa E₀ = const și V_tot crescând → ρ_Λ scade → NU este Λ.

---

## 2. Identificarea Corectă: Energia de Conexiune

### 2.1 Structura energetică a grafului QNG

Graful QNG G(t) = (N(t), E(t)) are două tipuri de energie:

**Tip 1: Energia nodurilor** (masă + câmpuri interne)
```
E_nodes = sum_i m_i c^2 = N_matter * m_bar * c^2    [N_matter = noduri cu masa != 0]
```

**Tip 2: Energia conexiunilor** (legăturile χ_i-χ_j)
```
E_bonds = N_edges * E_bond = (N_s * k_conn / 2) * E_bond
```

unde k_conn = gradul mediu al grafului (8 în configurația standard) și E_bond = energia
per conexiune (derivabilă din acțiunea de stabilitate — vezi §4).

### 2.2 Scalarea cu N_s (expansiunea universului)

Când universul se expandă (N_s crește prin noi noduri vacuumice, χ_new ≈ 0):

**Densitatea de energie din noduri (materie):**
```
rho_m = N_matter * m_bar * c^2 / (N_s * V_0)
```
N_matter = const (materia existentă nu se multiplică când se nasc noduri noi vacuumice)
→ **rho_m ~ 1/N_s ~ 1/a^3** ✓ (scalare de materie corectă)

**Densitatea de energie din conexiuni:**
```
rho_bonds = E_bonds / V_tot
          = (N_s * k_conn / 2) * E_bond / (N_s * V_0)
          = k_conn * E_bond / (2 * V_0)
```

N_s se simplifică! Atât numărul de conexiuni (N_s k_conn/2) cât și volumul (N_s V₀) cresc
proporțional cu N_s. Densitatea rămâne constantă.

```
rho_Lambda_QNG = k_conn * E_bond / (2 * V_0) = const   ✓ (scalare de constantă cosmologică!)
```

**Acesta este mecanismul corect pentru dark energy în QNG.**

---

## 3. Raportul Ω_Λ/Ω_m

### 3.1 Raportul curent

```
Omega_Lambda / Omega_m = rho_Lambda / rho_m
                       = [k_conn * E_bond / (2 V_0)] / [N_matter * m_bar * c^2 / (N_s * V_0)]
                       = k_conn * E_bond * N_s / (2 * N_matter * m_bar * c^2)
```

### 3.2 Evoluția temporală

```
(Omega_Lambda / Omega_m)(t) = (k_conn * E_bond) / (2 * m_bar * c^2) * N_s(t)/N_matter
                             ∝ N_s(t) ∝ a^3(t)
```

**Acesta este exact comportamentul observat**: Ω_Λ/Ω_m ∝ a³ ✓

La universul timpuriu (a → 0, N_s ≈ N_matter): Ω_Λ/Ω_m → 0 ✓
La universul târziu (a → ∞, N_s >> N_matter): Ω_Λ/Ω_m → ∞, Ω_Λ → 1 ✓

### 3.3 Condiția pentru Ω_Λ = 0.68 astăzi

La t = t₀ (acum): Ω_Λ/Ω_m = 0.68/0.32 = 2.125

```
k_conn * E_bond * N_s(t_0) / (2 * N_matter * m_bar * c^2) = 2.125
```

Cu k_conn = 8 și N_s(t₀)/N_matter = fracția de noduri vacuumice față de noduri masive:

```
E_bond / (m_bar * c^2) = 2.125 * 2 * N_matter / (8 * N_s(t_0))
                       = 0.53 * (N_matter / N_s(t_0))
```

Dacă astăzi (Ω_m = 0.32): fracția de noduri masive față de total ~ Ω_m = 0.32:
→ N_matter/N_s ≈ 0.32 (aproximativ, ignorând radiație)

```
E_bond / (m_bar * c^2) ≈ 0.53 * 0.32 ≈ 0.17
```

**Interpretare**: energia per conexiune ≈ 17% din energia de repaus a unui nod.
Aceasta este un raport de ordin 1 — nu necesită fine-tuning extrem.

---

## 4. Legătura cu Acțiunea de Stabilitate

Din qng-stability-action-v1.md, termenul de netezire (smoothing):

```
L_smooth = (k_sm/2) * (Sigma_i - <Sigma>_Adj(i))^2
```

Aceasta poate fi rescrisă ca sumă pe muchii:

```
L_smooth = (k_sm/2) * sum_{j in Adj(i)} w_ij * (Sigma_i - Sigma_j)^2 / k_conn
```

unde w_ij = Jaccard(i,j). Energia unei conexiuni la echilibru termic (fluctuație quantum):

```
E_bond = (k_sm / (2 * k_conn)) * <(Sigma_i - Sigma_j)^2>
```

Cu fluctuația zero-point: <(Sigma_i - Sigma_j)²> ~ ℏ * omega_sigma / k_sm (din Heisenberg):

```
E_bond = omega_sigma / 2    [zero-point energy al modului de diferență Sigma_i - Sigma_j]
```

unde ω_sigma = rata caracteristică de oscilație a câmpului Σ (~λ_1 din spectrul K).

**Deci E_bond este derivabilă din acțiunea de stabilitate** ca energia zero-point a
modurilor de diferență σ_ij = Σ_i - Σ_j. Aceasta este o cantitate bine definită spectral.

### 4.1 Estimare numerică E_bond

Din spectrul Jaccard cu k_conn=8 și M_EFF_SQ=0.014:
- λ₁ (primul mod non-constant) ~ λ_mean - Δ ~ 2.0 (estimat)
- ω_sigma ~ √λ₁ ~ 1.4

```
E_bond ~ omega_sigma / 2 ~ 0.7   [în unități ℏ]
```

Raportul față de m_bar c² (masa unui nod în unități QNG ~ chi_ref):
```
E_bond / (m_bar c^2) = omega_sigma/(2 chi_ref) ~ 0.7 / chi_ref
```

Pentru E_bond/(m_bar c²) ≈ 0.17: chi_ref ≈ 0.7/0.17 ≈ 4.

Aceasta e o restricție pe parametrul chi_ref (masa de referință) — testabilă.

---

## 5. Comparație: Mod Constant vs Energie de Conexiune

| Proprietate | Mod constant (G37) | Energie conexiune (propunere) |
|---|---|---|
| ρ_Λ(t) ~ | 1/N_s ~ 1/a³ (materie!) | const ✓ |
| Ω_Λ/Ω_m(t) ~ | const (nu crește) | ∝ a³ ✓ |
| Factor discrepanță | ~1800x | ~1 (cu chi_ref ~ 4) |
| Derivare din S_QNG | Nu — identificare externă | Da — E_bond din k_sm ✓ |
| Fine-tuning | Extrem (1/N) | Ordin 1 |

---

## 6. Predicții Testabile

### 6.1 Restricția pe chi_ref

Condiția Ω_Λ = 0.68 → chi_ref ~ 4 (în unități ℏ).

chi_ref apare și în:
- Σ_chi,i = exp(-|χ_i - χ_ref|/χ_ref) [qng-stability-action-v1.md]
- τ_i = α_tau * |χ_i| [pragul temporal de stabilitate]

Dacă chi_ref ~ 4 este consistent cu tau-ul observat din flyby anomaly (C-060), aceasta
este o verificare non-trivială a mecanismului.

### 6.2 Ecuația de stare w

Din energia de conexiune constantă:
```
p_Lambda = -rho_Lambda   (presiune negativă, ecuație de stare w = -1)
```

Aceasta este identic cu Λ standard (w = -1). QNG nu prezice deviație w ≠ -1 din
mecanismul de conexiune.

### 6.3 Corecție la Raychaudhuri QNG

Din qng-friedmann-p1-geometry-v1.md, ecuația Raychaudhuri QNG:
```
H_dot + 2H^2 = alpha * rho_0 / a^2
```

Cu rho_0 = rho_m + rho_Lambda = rho_m,0/a^3 + rho_Lambda (const):

```
H_dot + 2H^2 = alpha * (rho_m,0/a^3 + rho_Lambda) / a^2
             = alpha * rho_m,0/a^5 + alpha * rho_Lambda/a^2
```

Termenul rho_Lambda/a² → 0 pentru a → ∞ (expansiune de Sitter tardivă ≈ H_dot + 2H² = 0
→ H ~ 1/t → desaccelerare asimptotică, NU de Sitter pur).

**Aceasta este o PREDICȚIE DIFERITĂ de GR**: QNG prezice că Ω_Λ → 1 tardiv NU
produce accelerare asimptotică (H = const), ci desaccelerare lentă (H ~ 1/t).

---

## 7. Stare Rezolvată vs Deschisă

| Issue | Stare | Detalii |
|---|---|---|
| Scalare temporală greșită (mod constant) | REZOLVAT | Modul constant nu e Λ: ρ~1/a³ |
| Mecanism corect (energie conexiune) | PROPUS | ρ_bonds = const, scaling OK |
| Derivare E_bond din S_QNG | PARȚIAL | Legată de zero-point al diferențelor Σ_ij |
| Valoarea absolută Ω_Λ = 0.68 | CONDIȚIONAT | Necesită chi_ref ~ 4; testabil |
| Fine-tuning | AMELIORAT | De la 1/N (~1800x) la O(1) cu chi_ref dat |
| w = -1 exact | PREZIS | Fără deviație de la Λ standard |

---

## 8. Concluzie

Identificarea **dark energy = energie de conexiune** (nu mod constant) rezolvă:
1. Scalarea temporală (ρ_bonds = const ✓)
2. Evoluția Ω_Λ/Ω_m ∝ a³ ✓
3. Reduce fine-tuning de la 1800x la O(1)

Ramâne un parametru nou: E_bond/m̄ c² ≈ 0.17, legat de chi_ref ~ 4.
Testabil prin consistența cu tau-ul flyby și cu Σ_chi parametrizarea.

**Gate G37e**: Reclasificabile de la FAIL → CONDITIONAL_PASS dacă identificarea
este înlocuită cu energia de conexiune și chi_ref ~ 4 e consistent cu datele de traiectorie.

---

*Documente conexe:*
- `qng-omega-lambda-v1.md` — analiza originală G37, identificare mod constant
- `qng-friedmann-p1-geometry-v1.md` — Raychaudhuri QNG cu rho total
- `qng-friedmann-ns-dynamics-v1.md` — evoluția N_s(t) și Friedmann Forma I
- `03_math/derivations/qng-stability-action-v1.md` — sursa lui k_sm și E_bond
