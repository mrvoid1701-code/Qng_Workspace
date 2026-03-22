# QNG: Ecuația Friedmann din Dinamica N_s(t)

**Status**: DERIVARE COMPLETĂ (cu 1 ipoteză nedemonstt riguros — P-F1)
**Versiune**: v1
**Data**: 2026-03-22
**Dependințe**: C-029, C-103, C-104, qng-sigma-dynamics-v1.md, qng-stability-action-v1.md
**Continuă**: qng-friedmann-v1.md (P-F2)

---

## 1. Punctul de Plecare: Regulile de Naștere/Moarte (C-029)

Din C-029, la fiecare pas de timp:

```
if Sigma_i < Sigma_min:        → nodul i moare
if Sigma_i >= Sigma_birth AND coerenta:  → se naste un nod nou
Delta_k_i^+ = floor(beta_+ * max(0, Sigma_i - Sigma_grow))   [crestere conexiuni]
Delta_k_i^- = floor(beta_- * max(0, Sigma_shrink - Sigma_i))  [scadere conexiuni]
```

Starea unui nod: N_i = (V_i, chi_i, phi_i), activ dacă Σ_i ≥ Σ_min.

---

## 2. Limita Omogenă (Ansatz FRW)

Presupunem Σ(i, t) = Σ_0(t) uniform pe tot graful (fără gradient spatial).

Atunci **toți nodurile au aceeași rată de naștere și moarte**:

```
gamma_+(t) = rata de nastere per nod = f(Sigma_0(t))
gamma_-(t) = rata de moarte per nod  = g(Sigma_0(t))
```

Ecuația pentru numărul de noduri:

```
dN_s/dt = [gamma_+(Sigma_0) - gamma_-(Sigma_0)] * N_s(t)       [EQ-NS]
```

### 2.1 Forma Explicită a Ratelor

Din regulile C-029, în aproximația mean-field (Σ_0 continuu):

```
gamma_+(Sigma_0) = beta_birth * max(0, Sigma_0 - Sigma_birth)
gamma_-(Sigma_0) = beta_death * max(0, Sigma_min - Sigma_0)
```

Pentru regimul de expansiune (Σ_0 > Σ_birth > Σ_min):

```
gamma_+(Sigma_0) = beta_birth * (Sigma_0 - Sigma_birth)
gamma_-(Sigma_0) = 0
```

Deci EQ-NS devine:

```
dN_s/dt = beta_birth * (Sigma_0 - Sigma_birth) * N_s(t)         [EQ-NS-exp]
```

---

## 3. Ecuația Friedmann QNG — Forma I

Din definiția parametrului Hubble (C-104, §1.4 din qng-friedmann-v1.md):

```
H(t) = (1/3) * dN_s/dt / N_s = (1/3) * [gamma_+(Sigma_0) - gamma_-(Sigma_0)]
```

**Ecuația Friedmann QNG (forma I):**

```
╔══════════════════════════════════════════════════════════╗
║  H(t) = (beta_birth / 3) * (Sigma_0(t) - Sigma_birth)  ║
║                                                           ║
║  (în regimul de expansiune: Sigma_0 > Sigma_birth)       ║
╚══════════════════════════════════════════════════════════╝
```

**Interpretare**: Hubble este proporțional cu excesul câmpului de stabilitate față de pragul de naștere. Un univers se extinde atunci și numai atunci când Σ_0 > Σ_birth.

---

## 4. Ecuația de Mișcare pentru Σ_0(t)

### 4.1 Din EOM-Σ temporal (qng-sigma-dynamics-v1.md §7, OSD-3)

Extensia temporală a EOM-Σ:

```
□_g Σ = -∂²_t Σ + Δ_g Σ = α ρ
```

În limita omogenă (Σ_0 uniform → ∇Σ_0 = 0 → Δ_g Σ_0 = 0):

```
Σ̈_0(t) = -α ρ_0(t)                                             [EOM-Σ-cosm]
```

Cu α = 4πG_eff (din limita newtoniană, §3 din qng-sigma-dynamics-v1.md).

### 4.2 Legătura H → Σ_0 → Σ̈_0

Din Ecuația Friedmann Forma I:

```
Sigma_0(t) = Sigma_birth + 3H(t) / beta_birth
Sigma_dot_0 = 3 * H_dot / beta_birth
Sigma_ddot_0 = 3 * H_ddot / beta_birth
```

Substituind în EOM-Σ-cosm:

```
3 * H_ddot / beta_birth = -alpha * rho_0(t)
H_ddot = -(alpha * beta_birth / 3) * rho_0(t)                   [EQ-ACC]
```

---

## 5. Sistemul Friedmann Complet QNG

Avem acum **4 ecuații pentru 4 necunoscute** (H, Σ_0, ρ_0, p_0):

```
[F1]  H(t) = (beta_birth / 3) * (Sigma_0 - Sigma_birth)           [Hubble-Sigma]
[F2]  Sigma_ddot_0 = -alpha * rho_0                                [EOM-Σ temporal]
[F3]  rho_dot_0 = -3H(rho_0 + p_0)                                [conservare energie]
[F4]  p_0 = w * rho_0                                              [ecuatie de stare]
```

cu parametrii:
- β_birth: rata de naștere (din C-029, ~O(1))
- α = 4πG_eff (din limita newtoniană)
- w: parametrul ecuației de stare (w=0 materie, w=-1 DE)

**Aceasta este sistemul Friedmann QNG.**

### 5.1 Soluția pentru Materie Rece (w=0, ρ_0 ≠ 0)

Din [F3]: ρ̇_0 = -3H ρ_0 → ρ_0(t) = ρ_{0,0} / a(t)³

Din [F2]: Σ̈_0 = -α ρ_0

Diferențiind [F1]: Ḣ = (β_birth/3) Σ̇_0, Ḧ = (β_birth/3) Σ̈_0 = -(α β_birth/3) ρ_0

Deci:

```
H_ddot = -(alpha * beta_birth / 3) * rho_0                        [*]
```

Combinând cu ρ_0 ∝ N_s^{-1} = N_{s,0}^{-1} exp(-3∫H dt):

Pentru H ~ const (quasi-de Sitter): ρ_0 ~ const → Ḧ ~ const → H(t) ~ t²/2 * const

Aceasta nu e consistent cu H = const. Deci soluția quasi-de Sitter necesită ρ_0 → 0 (vacuum).

### 5.2 Soluția de Vid (ρ_0 → 0): de Sitter

Cu ρ_0 = 0: Σ̈_0 = 0 → Σ̇_0 = const → Σ_0(t) = Σ_∞ + c₁ t

Dar Σ_0 ∈ [0,1], deci c₁ = 0 → Σ_0 = const → H = const.

**Soluția de Sitter QNG**:

```
Sigma_0 = Sigma_DS = Sigma_birth + 3 H_DS / beta_birth = const
H_DS = (beta_birth / 3) * (Sigma_DS - Sigma_birth) = const
a(t) ~ exp(H_DS * t)
```

Aceasta este expansiunea exponențială (de Sitter) în QNG — fără constantă cosmologică externă,
ci din stabilitatea uniformă a câmpului Σ.

### 5.3 Soluția Dominată de Materie

Din [*] și ρ_0 = ρ_{0,0}/a³ = ρ_{0,0}/exp(3∫H dt):

Definim H = ȧ/a, deci ρ_0 = ρ_{0,0}/a³.

Ecuația [*] devine:

```
d²H/dt² = -(alpha * beta_birth / 3) * rho_{0,0} / a(t)^3
```

Cu a(t) = a_0 * (t/t_0)^(2/3) (soluție standard materie dominată):

```
a³ ~ t² → rho_0 ~ 1/t²
d²H/dt² ~ -C/t²
```

Integrând: H ~ C * ln(t) + ... Aceasta dă H → ∞ pentru t → 0 și H → 0 pentru t → ∞.
Comportament calitativ corect (Big Bang → materie → deselerare).

---

## 6. Conexiunea cu Spectrul și Ω_Λ

### 6.1 Densitate de energie în sistemul [F1-F4]

Sistemul Friedmann QNG conține ρ_0(t) ca densitate totală de energie (materie + dark energy).

Spectrul QNG dă:
```
rho_0 = rho_Lambda + rho_matter = E_vac / V_tot = (1/(2 N_s V_0)) * Sum_k sqrt(lambda_k)
```

### 6.2 De ce Ω_Λ ~ 1/N chiar și cu Friedmann corect

Din sistemul [F1-F4], densitatea critică (condiție de platitudine) este:

**Dacă** folosim proto-Friedmann H² = (8πG/3)ρ (analogie GR):
```
rho_crit = 3H² / (8 pi G_eff) = rho_tot    [univers plat]
Omega_Lambda = rho_Lambda / rho_crit = rho_Lambda / rho_tot
             = omega_0 / Sum_k omega_k
             ~ 1/N
```

**Dacă** folosim Friedmann QNG [F1]:
```
rho_crit depinde de relatia H - rho (care ramane nedeterminata fara P-F1)
```

**Concluzie**: În ambele cazuri, Ω_Λ = ρ_Λ/ρ_tot este un raport spectral.
Sistemul Friedmann nu modifică raportul ρ_Λ/ρ_tot, ci determină EVOLUȚIA lui în timp.

---

## 7. Problema P-F1: Legătura R_Forman → H

### 7.1 Ce nu merge cu Forman-Ricci

Pentru un graf ER cu N_s(t) noduri și grad mediu k:

```
<R_F>(t) = 4 - 2k + 2k²/N_s(t)
```

Derivând:
```
d<R_F>/dt = -2k² * dot_N_s / N_s² = -6H * k²/N_s(t)
```

Termenul 2k²/N_s(t) scade cu expansiunea → <R_F>(t) → (4-2k) = const.

**Concluzie**: Forman-Ricci curvature NU este analogul lui 6H² din GR.
Dimpotrivă, <R_F> tinde la o constantă în expansiune.

### 7.2 Ce ar trebui să fie

Ecuația Friedmann 1 în GR vine din G₀₀ = 8πG T₀₀ — componenta **temporală** a
tensorului Einstein. Aceasta implică **curbura extrinsecă** a hypersuprafețelor t=const
(K_ij ~ H δ_ij), nu curbura intrinsecă (R_Forman).

Analogul în QNG ar fi:
```
K_QNG ~ dg_ij/dt / (2g_ij) ~ H    [curbura extrinseca ~ H]
```

Pentru metrica QNG g_ij = (1-2Σ_0)δ_ij:
```
dg_ij/dt = -2Σ̇_0 δ_ij
K_QNG ~ Σ̇_0 / (1-2Σ_0) ≈ Σ̇_0    [pentru Sigma_0 << 1]
```

Din [F1]: Σ̇_0 = 3Ḣ/β_birth → K_QNG ~ Ḣ, nu H.

**Concluzie pentru P-F1**: Curbura extrinsecă K_QNG ~ Ḣ, nu H.
Ecuația Friedmann 1 (H²=8πGρ/3) necesită o altă derivare în QNG.

### 7.3 Ruta alternativă: Integrand acțiunea

Acțiunea QNG (qng-stability-action-v1.md):
```
S = Sum_t Sum_i [(k_cl/2)(Sigma_i - Sigma_hat_i)² + (k_sm/2)(Sigma_i - <Sigma>_adj)²
    + (k_chi/2)chi_i² + k_mix chi_i(Sigma_i - <Sigma>_adj) + k_phi(1-cos(phi_i-<phi>_adj))]
```

În limita omogenă (Σ_i = Σ_0, ⟨Σ⟩_adj = Σ_0, φ_i = ⟨φ⟩_adj):
```
L_i,t = (k_cl/2)(Sigma_0 - Sigma_hat_0)² + (k_chi/2)chi_0²
```

Termenul cinetic pentru Σ_0 apare doar prin extensia temporală (□_g Σ). Fără
derivata temporală explicită în acțiunea de stabilitate, H² nu apare direct.

**Aceasta confirmă că P-F1 necesită extinderea acțiunii de stabilitate cu un termen cinetic
explicit ∂_t Σ, sau o derivare separată a componentei G₀₀ a ecuației Einstein QNG.**

---

## 8. Rezumat: Ce Avem și Ce Lipsește

### Ce e derivat:

```
H(t) = (beta_birth/3) * (Sigma_0(t) - Sigma_birth)      [Friedmann QNG — Forma I]
Sigma_ddot_0 = -alpha * rho_0                             [EOM-Sigma cosmologic]
rho_dot_0 = -3H(rho_0 + p_0)                             [conservare energie]
```

Soluții:
- **de Sitter**: Σ_0 = const, H = const, a ~ e^{H t}
- **materie dominată**: H ~ 2/(3t), a ~ t^{2/3} (calitativ)

### Ce lipsește:

| Gap | Descriere | Impact |
|-----|-----------|--------|
| P-F1 | H² = (8πG/3)ρ din QNG | Nu știm dacă proto-Friedmann e corect |
| β_birth | Valoarea numerică a ratei de naștere | Necesară pentru H absolut |
| Σ_birth | Pragul de naștere (față de Σ_0 actual) | Necesară pentru H_0 |
| G_eff | Legătura α = 4πG_eff cu G Newton | Parțial din gate-uri, nu complet |

### Rezultatul central:

**Ω_Λ ~ 1/N este o identitate spectrală, independent de dinamica Friedmann.**
Ecuațiile Friedmann QNG sunt corect structurate și reproduc de Sitter + materie dominată,
dar nu pot repara problema Ω_Λ.

---

*Legătură cu documente existente:*
- `qng-friedmann-v1.md` — setup cosmologic, proto-Friedmann prin analogie
- `qng-omega-lambda-v1.md` — analiza detaliată discrepanță Ω_Λ
- `03_math/derivations/qng-c-029.md` — regulile de naștere/moarte
- `03_math/derivations/qng-sigma-dynamics-v1.md` — EOM-Σ (OSD-3: extensia temporală)
- `03_math/derivations/qng-stability-action-v1.md` — acțiunea de stabilitate
