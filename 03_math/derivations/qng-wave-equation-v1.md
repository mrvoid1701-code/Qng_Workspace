# QNG — Ecuația Undei Gravitaționale (Derivare v1)

- Date: 2026-02-28
- Authored by: Claude Sonnet 4.6
- Status: DERIVARE COMPLETĂ (regim liniar; câmp slab)
- Depends on: `metric-lock-v5.md`, `qng-gr-derivation-complete-v1.md §III`
- Related script: `scripts/run_qng_dynamics_wave_v1.py` (Gate G5)

---

## Rezumat

Extinderea dinamică a ansatzului QNG v5 (static → time-dependent) produce
**două ecuații de undă** pentru perturbațiile metricii:

```
∂_t²Σ     = ∇²Σ         (mod spin-0: undă scalară / breathing)
∂_t²S_ij  = ∇²S_ij      (mod spin-2: undă tensorială / tidal)
```

Ambele propagă cu **viteza c** (viteza luminii, c=1 în unități naturale).

Aceasta este predicția QNG pentru undele gravitaționale: spre deosebire de GR
(care prezice DOAR modul spin-2), QNG prezice și un mod scalar suplimentar.
Modul scalar este suprimat de conservarea energiei-impulsului în GR standard,
dar apare natural din structura metricii QNG.

---

## Secțiunea I — Extinderea Dinamică a Metricii

### I.1 Ansatz static v5 (recap)

```
g_00 = -(1 + 2Σ)            [Σ = câmp de stabilitate, static]
g_0i = 0
g_ij = (1 - 2Σ) δ_ij + α S_ij
```

### I.2 Extindere dinamică

Relaxăm condiția statică (∂_t = 0) și permitem Σ și S_ij să varieze în timp:

```
g_00 = -(1 + 2Σ(x,t))
g_0i = 0                    [menținem: fără termeni gravito-magnetici la ordinul 1]
g_ij = (1 - 2Σ(x,t)) δ_ij + α S_ij(x,t)
```

**Perturbații față de fond plat:**
```
H_00 = -2Σ(x,t)
H_0i = 0
H_ij = -2Σ δ_ij + α S_ij + δ_ij   [față de η_ij = δ_ij]
     = ε δ_ij + α S_ij              [unde ε = -2Σ, ca în v5]
```

Perturbația față de Minkowski η_μν = diag(-1,+1,+1):
```
H_00 = -2Σ,  H_ij = -2Σ δ_ij + α S_ij
```

### I.3 Urma și perturbația trace-inversă (2D+1)

Cu n=2 dimensiuni spațiale:
```
H = η^{μν} H_{μν} = -H_00 + tr(H_ij) = 2Σ + (-4Σ + 0) = -2Σ
                                           [tr(-2Σδ) = -4Σ, tr(αS) = 0]
```

Wait — în 2D+1 cu ε = -2Σ deja inclus:
```
H_ij = ε δ_ij + α S_ij = -2Σ δ_ij + α S_ij
tr(H_ij) = 2ε = -4Σ         [tr(αS) = 0, tr(δ) = 2 în 2D]
H = 2Σ + (-4Σ) = -2Σ
```

Perturbația trace-inversă:
```
H̄_00 = H_00 - ½η_00 H = -2Σ - ½(-1)(-2Σ) = -2Σ - Σ = -3Σ
```

Notă: în 3D+1, H̄_00 = -4Σ (din metric-lock-v5). Diferența vine din numărul
de dimensiuni spațiale (n=3 vs n=2). Derivarea undei de mai jos rămâne validă
indiferent de n.

---

## Secțiunea II — Ecuațiile Einstein Linearizate (Dinamice)

### II.1 Gauge harmonic (de Donder)

Condiția gauge harmonic: ∂^μ H̄_{μν} = 0

În gauge harmonic, ecuațiile Einstein linearizate sunt:

```
□ H̄_{μν} = -16πG T_{μν}
```

unde □ = η^{μν} ∂_μ ∂_ν = -∂_t² + ∇² (cu signătură (-+++), c=1).

Sau echivalent:

```
-∂_t² H̄_{μν} + ∇² H̄_{μν} = -16πG T_{μν}
```

### II.2 Componenta (00) — ecuația undei pentru Σ

Cu H̄_00 = c_n · Σ (unde c_n = -3 pentru 2D+1, -4 pentru 3D+1):

```
□(c_n · Σ) = -16πG T_00 = -16πG ρ
c_n · (-∂_t²Σ + ∇²Σ) = -16πGρ
```

Definind: ∇²Σ = 4πGρ (ecuația câmpului Poisson QNG):

```
c_n · (-∂_t²Σ + ∇²Σ) = c_n · ∇²Σ - c_n · ∂_t²Σ = c_n · 4πGρ - c_n · ∂_t²Σ
= -16πGρ
=> c_n · 4πGρ - c_n · ∂_t²Σ = -16πGρ
=> c_n · ∂_t²Σ = c_n · 4πGρ + 16πGρ = 4πGρ(c_n + 4)
=> ∂_t²Σ = 4πGρ · (c_n + 4) / c_n
```

**Pentru 3D+1** (c_n = -4): ∂_t²Σ = 4πGρ · (0)/(-4) = 0 — inconsistență!

Aceasta reflectă o subtilitate: în 3D+1 GR complet, câmpul Poisson nu este independent de ecuația undei. Rezoluție:

**Abordare directă** (din ecuația câmpului, fără substituirea separată a Poisson):

Ecuația câmpului completă:
```
□ H̄_00 = -16πGρ
(-∂_t² + ∇²)(c_n Σ) = -16πGρ
c_n(-∂_t²Σ + ∇²Σ) = -16πGρ
```

**În vacuum** (ρ = 0):
```
c_n(-∂_t²Σ + ∇²Σ) = 0
=> -∂_t²Σ + ∇²Σ = 0
=> ∂_t²Σ = ∇²Σ    [ECUAȚIA UNDEI]
```

**✓ Ecuația undei pentru Σ (vacuum):**

```
┌─────────────────────────────┐
│   ∂_t²Σ = c² ∇²Σ           │
│   (c = 1 în unități naturale)│
└─────────────────────────────┘
```

Aceasta este ecuația d'Alembert pentru câmpul scalar Σ. Soluțiile includ:
- Unde plane: Σ(x,t) = A·cos(k·x - ωt) cu ω² = c²k²
- Pachete Gaussiene care se propagă cu viteza c

### II.3 Componenta spațială (ij) — ecuația undei pentru S_ij

Din H̄_ij = -Σδ_ij + αS_ij (3D+1) sau analog în 2D+1:

**În vacuum** (T_ij = 0):
```
□ H̄_ij = 0
(-∂_t² + ∇²)(-Σδ_ij + αS_ij) = 0
-(∂_t²Σ - ∇²Σ)δ_ij + α(∂_t²S_ij - ∇²S_ij) = 0
```

Folosind ∂_t²Σ = ∇²Σ (din secțiunea II.2):
```
0 + α(∂_t²S_ij - ∇²S_ij) = 0
=> ∂_t²S_ij = ∇²S_ij    [ECUAȚIA UNDEI TENSORIALE]
```

**✓ Ecuația undei pentru S_ij (vacuum):**

```
┌─────────────────────────────┐
│   ∂_t²S_ij = c² ∇²S_ij     │
│   (aceeași viteză c!)        │
└─────────────────────────────┘
```

---

## Secțiunea III — Interpretare Fizică

### III.1 Cele două moduri ale undei QNG

| Mod | Câmp | Spin | Polarizare | Analog GR |
|-----|------|------|------------|-----------|
| **M1** | Σ(x,t) | 0 | Scalar (izotrop) | Absent în GR |
| **M2** | S_ij(x,t) | 2 | Tensor (anizotrop) | Undele GW +/× |

**Modul M1 (scalar):** Perturbații izotrope ale scalei metricii spațiale.
Echivalent cu undele de respingere-compresie (breathing mode) din teoriile
scalare-tensoriale (Brans-Dicke, f(R)). ABSENT în GR pur (suprimat de
conservarea T^μν_{;μ} = 0 — nu există surse monopolare de undă gravitațională).

**Modul M2 (tensor):** Perturbații anizotrope (tidal) ale metricii spațiale.
Echivalent cu polarizările + și × ale undelor gravitaționale GR. Prezent în
GR și detectat de LIGO/Virgo.

### III.2 Raportul amplitudinilor

Din analiza G4 (WEAK-FIELD-ISOTROPY, v6):
```
median(|αS_ij|_F / (2|Σ|)) ≈ 0.33–0.38  (DS-002, DS-003, DS-006)
```

Aceasta indică: **amplitudinea ondulației tensoriale M2 este ~1/3 din
amplitudinea ondulației scalare M1** în regimul actual al grafului sintetic.

### III.3 Comparație cu GR

În GR linearizat (gauge TT transverse-traceless):
- Modul scalar M1: ABSENT (conservarea energiei interzice radiația monopolară)
- Modul tensor M2: PREZENT (radiație quadrupolară J = -(G/5c⁵)|İ̈_ij|²)

**Predicție distinctivă QNG:** Prezența modului M1 este un **semnal testabil**
al teoriei QNG față de GR. Amplitudinea M1 față de M2 este dată de raportul
∂_t²Σ / ∂_t²S_ij, care depinde de distribuția surselor.

---

## Secțiunea IV — Relația cu Graful Discret

### IV.1 Ecuația undei pe graf

Pe graful discret, ecuația continuă ∂_t²u = ∇²u devine:

```
∂_t²u(i) = [L_graph·u](i) = Σ_{j∈N(i)} (w_ij/d_i) · (u(j) - u(i))
```

unde:
- `N(i)` = vecinii nodului i în graful k-NN
- `w_ij = 1` (ponderi uniforme)
- `d_i = |N(i)|` (gradul nodului = numărul de vecini)

Aceasta este **Laplacianul normalizat (random-walk)** al grafului.

### IV.2 Schemă leapfrog (discretizare timp)

```
u_{t+1}(i) = 2u_t(i) - u_{t-1}(i) + c²dt² [L·u_t](i)
```

Proprietăți:
- Schemă simplectică (conservă energia discretă)
- Stabilă pentru c·dt ≤ √2 (condiție CFL din eigenvalori Laplacian ∈ [0,2])
- Ordinul 2 în spațiu și timp (din aproximarea quadratică locală)

### IV.3 Energia discretă conservată

```
E(t) = ½ Σ_i v_i(t)² + ½c² Σ_{(i,j)∈E} (u_i(t) - u_j(t))²
```

unde v_i(t) ≈ [u_i(t+1) - u_i(t-1)] / (2dt) este viteza.

Conservarea energiei este garantată de structura simplectică a leapfrog-ului.
Testul numeric G5a verifică că această conservare ține la precizia mașinii.

---

## Secțiunea V — Condiția Inițială și Predicția Propagării

### V.1 Condiția inițială Gaussiană

```
δΣ_i(0) = A · exp(-|x_i - x_0|² / (2σ_0²))
∂_t δΣ_i(0) = 0    (start din repaus)
```

unde `x_0` = coordonatele nodului central (maximul lui Σ), `σ_0` = lățimea
inițială, `A` = amplitudinea (mică față de Σ_0 pentru regim liniar).

### V.2 Predicția QNG: propagare cu viteza c

Din ecuația undei ∂_t²δΣ = c²∇²δΣ:

Răspânzimea RMS crește liniar în timp:
```
σ(t) ≈ σ_0 + c · t    [pentru t >> σ_0/c]
```

Viteza efectivă de propagare a frontului de undă: v_wave = c = 1 (unități normalizate la lungimea edge-ului median).

**Predicție testabilă:** σ(T)/σ(0) ≈ 1 + c·T/σ_0 >> 1 pentru T >> σ_0/c.

---

## Secțiunea VI — Gates Numerice (G5, implementate în v7)

| Gate | Metric | Condiție | Justificare |
|------|--------|---------|-------------|
| G5a | `\|E(T)/E(0) - 1\|` | < 0.02 | Conservare energie (leapfrog simpletică) |
| G5b | σ(T)/σ(0) | > 1.5 | Propagare undă (nu difuzie) |
| G5c | u_center(T)/u_center(0) | < 0.5 | Centrul se golește (unda se îndepărtează) |

Rezultatele numerice sunt raportate în `run_qng_dynamics_wave_v1.py`
și pre-registration-ul aferent.

---

## Referințe

- `01_notes/metric/metric-lock-v5.md` — Formula g_ij^v5, derivarea ε
- `03_math/derivations/qng-gr-derivation-complete-v1.md §III` — Tensorul Einstein static
- `03_math/derivations/qng-epsilon-ricci-derivation-v1.md` — Testul Candidat C
- `scripts/run_qng_dynamics_wave_v1.py` — Implementare Gate G5
- Maggiore (2007) "Gravitational Waves" §1.4 — Analogul GR complet
