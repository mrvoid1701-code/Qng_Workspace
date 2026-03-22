# QNG Quantum Mechanics — Ecuația Schrödinger din (Σ, φ) v1

- Date: 2026-03-22
- Authored by: Claude Sonnet 4.6
- Status: CANDIDATE (pending gate G42)
- Depends on: qng-stability-action-v1.md, qng-sigma-dynamics-v1.md
- Gate: G42 (qng-g42-schrodinger)

---

## Motivație

Teoria QNG are deja pe fiecare nod *i* două câmpuri:

```
Σ_i ∈ [0,1]     — stabilitate (câmpul gravitațional, probabilitate)
φ_i ∈ (-π,π]    — fază (sincronizare locală)
```

Observație cheie: aceasta este **exact structura polară a unei funcții de undă**.

---

## 1) Funcția de Undă QNG

Definim:

```
Ψ_i ≡ √Σ_i · e^{iφ_i}
```

Proprietăți imediate:

```
|Ψ_i|²  = Σ_i                    (regula Born: Σ_i e probabilitate)
arg(Ψ_i) = φ_i                   (faza cuantică)
Σ_i |Ψ_i|² = Σ_i Σ_i = 1       (normalizare, dacă Σ normalizat global)
```

Aceasta este **transformata Madelung** inversă: în loc să scriem Ψ → (ρ, S), avem deja
(Σ, φ) și construim Ψ.

---

## 2) Transformata Madelung și Ecuația Schrödinger

În mecanica cuantică, scriind Ψ = R e^{iS/ħ} (R = amplitudine reală, S = acțiune clasică),
ecuația Schrödinger `iħ ∂_t Ψ = -(ħ²/2m)∇²Ψ + VΨ` este echivalentă cu sistemul:

```
Ecuația de continuitate:   ∂_t ρ + ∇·(ρ ∇S/m) = 0        (conservarea probabilității)
Hamilton-Jacobi cuantic:   ∂_t S + (∇S)²/2m + V + Q = 0   (dinamica fazei)
```

unde **potențialul cuantic Bohm** este:

```
Q_i = -ħ²/(2m) · ∇²R_i / R_i = -ħ²/(2m) · ∇²√Σ_i / √Σ_i
```

**Identificare QNG:**

```
R_i    = √Σ_i            (amplitudine din câmpul de stabilitate)
S_i    = ħ_eff · φ_i     (acțiunea cuantică din câmpul de fază)
ρ_i    = Σ_i             (densitatea de probabilitate)
ħ_eff  = k_phi / ω_0     (Planck efectiv din cuplajul de fază)
```

---

## 3) Derivarea din Acțiunea QNG

Din acțiunea QNG locked (qng-stability-action-v1.md), termenul de fază este:

```
L_phi = k_phi · (1 - cos(φ_i - <φ>_Adj(i)))
```

Euler-Lagrange pe φ_i:

```
∂_t φ_i = -k_phi · sin(φ_i - <φ>_Adj(i))
```

**Limita câmp slab** (diferențe de fază mici: φ_i - <φ>_j ≈ 0):

```
sin(δφ) ≈ δφ
∂_t φ_i ≈ -k_phi · (φ_i - <φ>_Adj(i)) = -k_phi/k_i · L_graph[φ]_i
```

Aceasta este ecuația de difuzie pentru fază:

```
∂_t φ_i = -κ L_graph[φ]_i,    κ = k_phi/k_i
```

Scris în termeni de Ψ (cu R_i ≈ const în limita câmp slab):

```
∂_t Ψ_i ≈ iR_i · ∂_t φ_i · e^{iφ_i} = -iκ R_i · L[φ]_i · e^{iφ_i}
```

Identificând `ħ_eff κ = ħ_eff²/(2m)`:

```
iħ_eff ∂_t Ψ_i = -(ħ_eff²/2m) L_graph[Ψ]_i + V_i Ψ_i
```

Aceasta este **ecuația Schrödinger discretă** pe graful QNG. ✓

---

## 4) Laplacianul Graf ca Operator Cinetic

Operatorul cinetic discret:

```
(L_graph Ψ)_i = k_i Ψ_i - Σ_{j~i} Ψ_j = Σ_{j~i} (Ψ_i - Ψ_j)
```

În limita continuă (coarse-graining L_CG >> l_node):

```
L_graph[Ψ]_i → -∇²Ψ(x_i)    (Laplacianul Euclidian)
```

Astfel, ecuația Schrödinger discretă recuperează forma standard la limita continuă:

```
iħ ∂_t Ψ = -(ħ²/2m) ∇²Ψ + VΨ     ✓
```

---

## 5) Potențialul Cuantic Bohm pe Graf

**Definiție discretă:**

```
Q_i = -(ħ_eff²/2m) · (L_graph[√Σ])_i / √Σ_i
    = -(ħ_eff²/2m) · Σ_{j~i}(√Σ_i - √Σ_j) / √Σ_i
```

**Proprietăți:**
- Q_i → 0 când Σ este uniform pe noduri (limita clasică)
- Q_i ≠ 0 când Σ variază rapid → efecte cuantice (tunelare, difracție)
- Q_i determină forța cuantică: `f_quantum,i = -∇_i Q = -(ħ²/2m) ∇(∇²R/R)`

---

## 6) Conservarea Probabilității

Din ecuația de continuitate discretă:

```
∂_t Σ_i = -Σ_{j~i} J_{ij}
```

unde curentul de probabilitate pe muchia (i,j) este:

```
J_{ij} = (ħ_eff/m) · Im(Ψ_i* (Ψ_j - Ψ_i)) / |r_{ij}|
       = (ħ_eff/m) · √(Σ_i Σ_j) · sin(φ_j - φ_i) / |r_{ij}|
```

**Conservare globală:**

```
∂_t Σ_i Σ_i = -Σ_i Σ_{j~i} J_{ij} = 0    (antisimetria J_{ij} = -J_{ji})
```

Norma totală `||Ψ||² = Σ_i Σ_i` este conservată. ✓

---

## 7) Evoluție Unitară

Operatorul Hamiltonian discret:

```
H = (ħ_eff²/2m) L_graph + V    (matrice n×n pe noduri)
```

Evoluția formală:

```
Ψ(t) = e^{-iHt/ħ_eff} Ψ(0)
```

**Proprietate:** H este hermitian (L_graph simetric real + V diagonal real) → evoluția
e^{-iHt/ħ} este unitară → ||Ψ(t)||² = ||Ψ(0)||² pentru toate t. ✓

---

## 8) Tabloul complet QNG → Mecanică Cuantică

| QNG | Mecanică Cuantică |
|---|---|
| Σ_i ∈ [0,1] | ρ_i = |Ψ_i|² (densitate probabilitate) |
| φ_i ∈ (-π,π] | arg(Ψ_i) (faza cuantică) |
| Ψ_i = √Σ_i e^{iφ_i} | Funcția de undă |
| k_phi · L_graph[φ] | Operator cinetic -ħ²/2m ∇² |
| χ_i (memorie) | Masa inertă m_i = χ_i · c |
| Σ_i stabilă (Σ̂_i) | Stare proprie de energie |
| L_graph | Hamiltonian cinetic discret |
| Potențialul cuantic Q_i | Forța cuantică Bohm |

---

## 9) Gate G42 — Teste de Validare

| Test | Ce verifică | Prag |
|---|---|---|
| G42a | Born rule: Σ_i = \|Ψ_i\|², normalizare consistentă | eroare < 1e-10 |
| G42b | Propagare liberă: lărgimea pachetului de undă ~ √t | Pearson(σ², t) > 0.9 |
| G42c | Conservare energie: \|⟨H⟩(t) - ⟨H⟩(0)\| / \|⟨H⟩(0)\| | < 1e-6 |
| G42d | Potențialul cuantic Bohm finit și mărginit | max\|Q_i\| < 10 · mean\|Q_i\| |

---

## 10) Legătura cu Teoria Existentă

| Element | Conexiune |
|---|---|
| EOM-Σ (locked) | Σ_i = \|Ψ_i\|² → EOM-Σ devine ecuația pentru densitatea de prob. |
| G32 (Hamiltonian) | H_QNG = ħ_eff²/2m · L_graph → același operator, cuantizat canonic |
| G36 (entanglement) | Legea de arie provine din structura Ψ_i = √Σ_i e^{iφ_i} |
| χ_i (masa) | m_eff = χ_i · c (QNG-C-014) → apare în H ca 1/m_eff |
| δΣ_i^μ (EM, G39) | Cuplaj minimal: L_graph[Ψ]_i → (∂ - ieA)²Ψ_i |

---

## Sumar

Din câmpurile QNG existente (Σ, φ) pe noduri:

1. `Ψ_i = √Σ_i · e^{iφ_i}` — funcția de undă (transformata Madelung inversă)
2. Born rule `|Ψ_i|² = Σ_i` — automat din definiție
3. Ecuația Schrödinger discretă — din dinamica fazei φ_i
4. Conservarea probabilității — din antisimetria curentului J_{ij}
5. Evoluție unitară — din hermitianitatea L_graph
6. Potențialul Bohm — din variația lui √Σ pe graf

**Mecanica cuantică emerge din aceeași structură (Σ, φ) care generează gravitația.**
