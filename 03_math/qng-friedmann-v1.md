# QNG: Ecuațiile Friedmann — Derivare din Primele Principii

**Status**: DERIVARE PARȚIALA — pașii 1-4 completi, pasul 5 (legătura R→H) identificată ca lipsă
**Versiune**: v1
**Data**: 2026-03-22
**Dependințe**: C-103, C-104, C-109, metric-lock-v5, paper-gr-qm-strict-submit-en.md §3.3

---

## Motivație

Ecuațiile Friedmann în GR:

```
H² = (8πG/3) ρ                    [Friedmann 1 — expansiune]
ä/a = -(4πG/3)(ρ + 3p)            [Friedmann 2 — accelerație]
```

provin din ecuația Einstein G_μν = 8πG T_μν aplicată metricii FRW (omogenă, izotropă).

În QNG există deja:
- Un analog al ecuației Einstein: R(i) ≈ 2Λ + 16πG_eff ρ(i) (gate GR, §3.3 din paper)
- Un factor de scară: a(t) = (N_s(t)/N_s(t₀))^(1/3) (C-104)
- Energii de mod: E_k = ω_k/2 din spectrul K = L_Jaccard + m²I

Ce **lipsește**: conexiunea explicită R_QNG(t) = f(H(t), ä(t)/a(t)).

Scopul acestui document: derivăm pașii cât mai departe posibil și identificăm exact unde
se oprește derivarea actuală.

---

## 1. Ansatzul Cosmologic (FRW în QNG)

### 1.1 Câmpul uniform

Universul homogen în QNG corespunde câmpului Σ uniform:

```
Σ(i, t) = Σ₀(t)   pentru orice nod i    [condiție FRW]
```

Nu există direcție preferată → modul constant φ₀ = [1/√N] domină (k=0 în spectru).

Graful crește: N_s(t) = numărul de noduri stabile la momentul t.

### 1.2 Metrica FRW din metric-lock-v5

În limita izotropă (S_ij = 0, câmp uniform):

```
g_ij(t) = (1 - 2Σ₀(t)) δ_ij
```

Aceasta este exact metrica FRW conformă cu factor de scară:

```
a²(t) = 1 - 2Σ₀(t)    [din metric-lock-v5, limita izotropă]
```

### 1.3 Două definiții de a(t) — condiție de consistență

Din C-104 (volumetric):
```
a_vol(t) = (N_s(t)/N_s(t₀))^(1/3)
```

Din metric-lock-v5 (metric):
```
a_met(t) = √(1 - 2Σ₀(t))
```

**Condiție de consistență** (necesară, neverificată încă):
```
N_s(t)/N_s(t₀) = (1 - 2Σ₀(t))^(3/2)
```

Aceasta leagă dinamica câmpului Σ₀(t) de creșterea grafului.

### 1.4 Parametrul Hubble

Din definiția a_vol(t):

```
H(t) = ȧ/a = (1/3) * d/dt [ln N_s(t)] = (1/3) * Ṅ_s/N_s
```

---

## 2. Densitatea de Energie din Spectrul QNG

### 2.1 Energie totală de vacuum

Câmpul scalar cuantic pe graful Jaccard are energie de punct zero:

```
E_vac = (1/2) Σ_k ω_k = (1/2) Σ_k √λ_k
```

unde suma merge peste toți K_eff moduri incluși (constant + bottom + top).

### 2.2 Volumul fizic

Din C-103, volumul total al grafului:

```
V_tot(t) = N_s(t) * V̄(t) ≈ N_s(t) * V₀    [în limita V̄ constant, C-104]
```

unde V₀ = volumul unitar per nod.

### 2.3 Densitatea de energie

```
ρ_QNG(t) = E_vac / V_tot = (1 / (2 N_s(t) V₀)) * Σ_k √λ_k
```

### 2.4 Descompunere în componente

```
ρ_Λ  = ω₀ / (2 N_s V₀) = √(M_EFF_SQ) / (2 N_s V₀)    [modul constant]
ρ_m  = (1/(2 N_s V₀)) * Σ_{k≥1} √λ_k                  [toate celelalte moduri]
ρ_QNG = ρ_Λ + ρ_m
```

### 2.5 Fracția Ω_Λ — rezultat cheie

**Indiferent de valoarea lui G, V₀, sau orice altă constante:**

```
Ω_Λ = ρ_Λ / ρ_QNG = ω₀ / Σ_k ω_k = √λ₀ / Σ_k √λ_k
```

Aceasta este un **raport pur spectral** — nu depinde de G_eff, V₀, sau normalizare.

Numeric (N=280, spectrul Jaccard, M_EFF_SQ=0.014):
```
ω₀ = √0.014 = 0.1183
Σ_k ω_k ≈ N * ω_mean ≈ 280 * 2.1 ≈ 588
Ω_Λ ≈ 0.1183 / 588 ≈ 0.000201
```

Valoarea din G37: Ω_Λ_QNG = 0.000380 (valoare exactă din spectrul calculat).

**Concluzie structurală**: Ω_Λ ~ ω₀/(N * ω_mean) ~ 1/N.
Derivarea ecuațiilor Friedmann nu poate repara această discrepanță —
Ω_Λ este fixat de spectru, nu de dinamică.

---

## 3. Ecuația Einstein în QNG (Existentă)

Din paper §3.3 (gate G-Hamiltonian):

```
R(i) ≈ 2Λ_eff + 16πG_eff * ρ(i)
```

unde:
- R(i) = curbura Forman-Ricci la nodul i
- Λ_eff = constanta cosmologică efectivă (din spectru, ~0)
- G_eff = constanta gravitației efectivă (fitată numeric)

**Valori din G-Hamiltonian gate** (N=280, Jaccard):
- G_eff determinat numeric prin fit linear R(i) vs ρ(i)
- R² ≈ 0.057 (fit slab, dar semnificativ nonzero)

### 3.1 Limita omogenă (FRW)

Pentru Σ(i) = Σ₀(t) uniform:
```
R(i) = R₀(t) = const pentru orice i
ρ(i) = ρ₀(t) = const pentru orice i
```

Ecuația Einstein devine:
```
R₀(t) = 2Λ_eff + 16πG_eff * ρ₀(t)    [EQ-1]
```

---

## 4. Proto-Ecuația Friedmann

### 4.1 Legătura R_QNG → H (piesa lipsă)

În GR plat FRW, scalarul Ricci este:
```
R_GR = 6(ä/a + H²)                    [GR standard]
```

și G_00 = 3H² (componenta temporală a tensorului Einstein).

Pentru a obține ecuația Friedmann din QNG, avem nevoie de:
```
R_QNG(t) = f(H(t), ä(t)/a(t))         [NEDEMONSTRATĂ]
```

**Argumentul de analogie** (nu demonstrație riguroasă):

Dacă R_QNG se comportă ca R_GR în limita continuă (suportat de d_s ≈ 4 din Jaccard),
atunci la leading order în H:

```
R_QNG(t) ≈ 6(ä/a + H²) ≈ 6H²    [în materie-dominat sau H² >> ä/a]
```

Substituind în EQ-1:
```
6H² ≈ 2Λ_eff + 16πG_eff * ρ₀
H² ≈ Λ_eff/3 + (8πG_eff/3) * ρ₀    [proto-Friedmann QNG]
```

Aceasta reproduce structura ecuației Friedmann standard cu G = G_eff.

### 4.2 Ecuația accelerației (proto-Raychaudhuri)

Similar, din G_ii = -8πG T_ii (componenta spațială):
```
2ä/a + H² ≈ -8πG_eff * p    [presiune]
=> ä/a ≈ -(4πG_eff/3)(ρ + 3p)    [proto-Raychaudhuri]
```

### 4.3 Ecuația de continuitate

Conservarea T_μν: ∇_μ T^μν = 0 în QNG corespunde conservării energiei spectrale:
```
dρ/dt + 3H(ρ + p) = 0
```

Pentru modul constant (p = -ρ, stare de ecuație w = -1):
```
dρ_Λ/dt + 3H(ρ_Λ - ρ_Λ) = dρ_Λ/dt = 0    ✓  [constantă, ca în Lambda-CDM]
```

---

## 5. Tabelul Complet de Corespondențe

| Cantitate GR | Formula GR | Analog QNG | Status |
|-------------|-----------|------------|--------|
| Metrica FRW | a²(t) η_μν | g_ij = (1-2Σ₀)δ_ij | Metric-lock-v5 ✓ |
| Factor scară | a(t) | (N_s/N_s₀)^(1/3) | C-104 ✓ |
| Hubble H | ȧ/a | (1/3)Ṅ_s/N_s | Derivat ✓ |
| Densitate ρ | ρ_matter + ρ_Λ | E_vac/V_tot | Derivat §2 ✓ |
| Ω_Λ | ρ_Λ/ρ_crit | ω₀/Σω_k ≈ 1/N | Calculat — FAIL |
| Ecuația Einstein | G_μν = 8πGT_μν | R ≈ 2Λ + 16πG_eff ρ | Gate G-Ham ✓ |
| Friedmann 1 | H² = (8πG/3)ρ | H² ≈ (8πG_eff/3)ρ | Analogie ⚠️ |
| R_QNG → H | R = 6(ä/a+H²) | R_QNG = ? | **LIPSĂ** ❌ |
| Dinamica N_s(t) | — | Ṅ_s = f(Σ₀,τ,χ) | **LIPSĂ** ❌ |
| Presiunea p | -ρ (DE), 0 (CDM) | din spectru ρ_k | Parțial ⚠️ |

---

## 6. Problemele Deschise

### P-F1 (CRITICĂ): Derivarea R_QNG(t) = f(H, ä/a)

Trebuie arătat că curbura Forman-Ricci a unui graf omogen cu N_s(t) noduri
se reduce la 6(ä/a + H²) în limita continuă.

**Abordare posibilă**: Curbura medie Forman-Ricci pentru un graf ER cu N noduri și
grad mediu k are forma:

```
<R_F> = 4 - 2k + 2k²/N(t)
```

Termenul k²/N(t) variază în timp ca N⁻¹ → comportament H² potențial.

**Trebuie demonstrat**:
```
d/dt [k²/N_s(t)] ~ H²    (sau alte combinații)
```

### P-F2 (CRITICĂ): Dinamica N_s(t) din acțiunea QNG

Ecuația de mișcare pentru N_s(t) nu este derivată. Aceasta este echivalentul
ecuației Friedmann propriu-zise — cum crește graful în timp?

Din C-103: ΔN_s depinde de Σ, τ, χ prin regulile de naștere/moarte.
**Trebuie**: un sistem de ecuații diferențiale pentru (N_s, Σ₀, k_mean)(t).

### P-F3 (STRUCTURALĂ): Ω_Λ ~ 1/N

Chiar cu o derivare completă, Ω_Λ = ω₀/Σ_k ω_k ~ 1/N este o identitate spectrală,
independentă de G sau V₀. Nu poate fi reparată prin dinamică.

**Necesită**: un mecanism fizic care modifică raportul spectral ω₀/Σω_k.
Opțiuni (din qng-omega-lambda-v1.md):
- Condensat de vacuum (mai multe moduri la λ₀)
- Redefinirea ρ_Λ în termeni non-spectrali
- Mecanismul de desincronizare C-109 (accelerație fără Λ)

---

## 7. Concluzie

**Ce s-a demonstrat**:
1. Metrica FRW în QNG = limita izotropă a metric-lock-v5: g_ij = (1-2Σ₀)δ_ij
2. Parametrul Hubble H = (1/3)Ṅ_s/N_s din definiția volumetrică a lui a(t)
3. Densitatea de energie ρ_QNG = E_vac/V_tot din spectrul Jaccard
4. Proto-Friedmann H² ≈ (8πG_eff/3)ρ prin analogie cu R_GR (nedemonstrat riguros)
5. **Ω_Λ = ω₀/Σω_k ~ 1/N este o limitare structurală spectrală**, nu dinamică

**Ce lipsește**:
1. Derivarea riguroasă R_Forman → 6H² pentru grafuri în expansiune (P-F1)
2. Ecuația de mișcare pentru N_s(t) din acțiunea QNG (P-F2)
3. Mecanismul pentru Ω_Λ = 0.68 (P-F3, OPEN_PROBLEM)

**Implicație pentru G37e**: Problema Ω_Λ nu este rezolvabilă prin ecauțiile Friedmann.
Ecuațiile Friedmann clarifică structura (Ω_Λ este raport spectral, nu parametru liber),
dar nu o repară. Este necesară o extensie a teoriei.

---

*Legătură cu documente existente:*
- `qng-omega-lambda-v1.md` — analiza detaliată a discrepanței Ω_Λ
- `qng-neff-modes-v1.md` — derivarea ferestrei de moduri fizice
- `03_math/derivations/qng-c-103.md`, `qng-c-104.md` — scale factor din volumetrie
- `01_notes/metric/metric-lock-v5.md` — metrica cu modul conformal
- `06_writing/paper-gr-qm-strict-submit-en.md §3.3` — ecuația Einstein în QNG
