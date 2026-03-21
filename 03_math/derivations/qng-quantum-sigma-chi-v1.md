# QNG — Cuantificarea câmpurilor Σ și χ (v1)

- Date: 2026-03-21
- Status: exploratoriu — propunere teoretică, nu parte din lane-ul oficial
- Scope: cuantificarea canonică a câmpurilor Σ și χ pe graful Jaccard
- Related scripts: `scripts/run_qng_q_fields_v1.py`
- Related derivations: `qng-stability-theorems-v1.md`, `qng-cv-physical-origin-v1.md`, `run_qng_g17_v2.py`

---

## 1) Situația actuală în QNG (semiclasic)

QNG este în prezent **semiclasic**:

```
Graful G = (V, E)           ← substrat cuantic (eigenmodes, ε_vac, G17/G18)
       ↕  cuplaj G20 (one-loop)
Câmpurile Σ_i, χ_i, φ_i    ← clasice (gradient descent, valori bine-definite per nod)
```

Cuantificarea e parțială: **graful poartă fluctuații cuantice** (vacuum zerotil G17,
back-reaction semiclasică G20), dar câmpurile pe el au valori ascuțite la fiecare pas.

---

## 2) Propunere: cuantificarea câmpurilor

Tratăm Σ și χ ca câmpuri cuantice pe graful fix G.

### 2.1) Acțiunea clasică per nod (din `qng-stability-theorems-v1.md`)

```
S_i = k_cl/2 · (Σ_i - Σ̂_i)²
    + k_sm/2 · Σ_{j ∈ Adj(i)} (Σ_i - Σ_j)²
    + k_chi/2 · χ_i²
    + k_mix · χ_i · (Σ_i - ⟨Σ⟩_{Adj(i)})
```

### 2.2) Hamiltonianul cuantic (cuantificare canonică)

Introducem impulsurile conjugate:

```
p_Σ,i = ∂L/∂(∂_t Σ_i)     cu  [Σ̂_i, p̂_Σ,j] = iħ δ_ij
p_χ,i = ∂L/∂(∂_t χ_i)     cu  [χ̂_i, p̂_χ,j] = iħ δ_ij
```

Hamiltonianul total:

```
Ĥ = Σ_i [p̂_Σ,i² / (2m_Σ) + p̂_χ,i² / (2m_χ)] + V̂(Σ, χ)

V̂ = 1/2 · [Σ, χ] K [Σ, χ]ᵀ
```

unde **matricea potențialului** K este (2N × 2N):

```
K = ┌ k_cl · I + k_sm · L    k_mix · I ┐
    └ k_mix · I               k_chi · I ┘
```

cu L = Laplacianul grafului G (N × N), m_Σ = m_χ = 1 (unități naturale).

---

## 3) Moduri normale

Diagonalizând K:

```
K v_a = λ_a v_a     (a = 1, ..., 2N)
ω_a = √λ_a
```

Hamiltonianul devine suma de 2N oscilatori armonici independenți:

```
Ĥ = Σ_a ħ ω_a (â†_a â_a + 1/2)
```

### 3.1) Condiția de stabilitate cuantică

Sistemul e cuantic-stabil dacă și numai dacă **toți λ_a > 0**, adică:

```
K pozitiv definit  ⟺  k_chi > k_mix² / k_cl_eff
```

unde `k_cl_eff = k_cl + k_sm λ_min(L)`. Aceasta înlocuiește condiția clasică `|a_chi| < 1`.

### 3.2) Energia zero-point

```
E_0 = ħ/2 · Σ_a ω_a
```

Include contribuții atât din câmpul Σ cât și din χ, cuplate prin k_mix.

---

## 4) Observabile cuantice

### 4.1) Fluctuații zero-point per nod

Fie U_a^Σ(i) și U_a^χ(i) componentele Σ și χ ale eigenvectorului a.

```
⟨(δΣ_i)²⟩ = ħ/2 · Σ_a [U_a^Σ(i)]² / ω_a

⟨(δχ_i)²⟩ = ħ/2 · Σ_a [U_a^χ(i)]² / ω_a
```

### 4.2) Corelații încrucișate Σ-χ (indicator de entanglement)

```
⟨δΣ_i · δχ_i⟩ = ħ/2 · Σ_a U_a^Σ(i) · U_a^χ(i) / ω_a
```

- Dacă `k_mix = 0`: U_a^Σ și U_a^χ sunt ortogonale → `⟨δΣ δχ⟩ = 0` (necorelat)
- Dacă `k_mix ≠ 0`: apare un unghi de mixare θ ≠ 0 → `⟨δΣ δχ⟩ ≠ 0` (corelat cuantic)

Aceasta este **entanglement local Σ-χ** generat de cuplajul k_mix.

---

## 5) Modificarea coeficientului cv

**cv clasic** (din `qng-cv-physical-origin-v1.md`):

```
cv_cl = σ(ε_vac) / μ(ε_vac)  ≈ 0.405
```

provine din fluctuațiile eigenmodeurilor grafului (Porter-Thomas).

**cv cuantic** (nou):

```
cv_q = σ(⟨(δΣ_i)²⟩_i) / μ(⟨(δΣ_i)²⟩_i)
```

măsoară **inhomogeneitatea spațială a fluctuațiilor zero-point ale lui Σ**.

### 5.1) Cele două niveluri de fluctuații

```
cv_total² ≈ cv_cl²  +  cv_q²   (în limita fluctuațiilor mici)
```

- `cv_cl` ← fluctuații ale eigenmodeurilor grafului (cuantificarea grafului, G17)
- `cv_q`  ← fluctuații ale câmpului Σ în sine (cuantificarea câmpului, **prezenta lucrare**)

Dacă `cv_q ≪ cv_cl`: cuantificarea câmpului e o corecție minoră.
Dacă `cv_q ~ cv_cl`: ambele scale sunt comparabile → trebuie revizuit calculul Pioneer.

---

## 6) Implicații pentru teoremele de stabilitate

| Teoremă clasică (v1) | Echivalent cuantic |
|---|---|
| **B** Σ_i ∈ [0,1] (invarianță clip) | Înlocuită de spectru mărginit al Ĥ (Ĥ ≥ 0) |
| **C** \|a_chi\| < 1 (non-runaway χ) | K pozitiv definit → spectral gap > 0 |
| **D** Moment de ordin 2 mărginit | ⟨χ²⟩ < ∞ → garantat dacă ω_min > 0 |
| **F** Descreștere potențial | Starea fundamentală Ĥ \|0⟩ = E_0 \|0⟩ stabilă |

> **Notă:** Teorema B nu mai e garantată prin clip — în formularea cuantică,
> Σ poate ieși din [0,1] ca operator. Soluție: potențial de confinement
> `V_conf(Σ) = λ · (Σ(1-Σ))⁻¹` care înlocuiește clip-ul.

---

## 7) Conexiunea cu G17 (cuantificarea grafului)

G17 cuantifică **graful** prin Hamiltonianul spectral al Laplacianului:

```
Ĥ_G17 = Σ_k ħ Ω_k (b†_k b_k + 1/2)     Ω_k ∝ √λ_k(L)
```

Prezenta lucrare cuantifică **câmpurile pe graf**:

```
Ĥ_q-fields = Σ_a ħ ω_a (â†_a â_a + 1/2)     ω_a = √λ_a(K)
```

Diferența: eigenmodeurile lui K depind atât de L cât și de (k_cl, k_chi, k_mix).
La k_mix = 0: eigenmodeurile K se factorizează în moduri Σ pure și moduri χ pure.
La k_mix ≠ 0: modurile sunt amestecuri Σ-χ.

---

## 8) Două scale Planck

Dacă cuantifici atât graful cât și câmpurile:

```
ħ_graf    ← controlează cuantizarea grafului (G17, eigenmodes L)
ħ_câmp    ← controlează cuantizarea câmpurilor Σ, χ (prezenta lucrare)
```

Raportul `r = ħ_câmp / ħ_graf` este un parametru nou al teoriei.

- `r → 0`: recuperezi teoria semiclasică actuală (câmpuri clasice, graf cuantic)
- `r = 1`: teorie complet cuantică (singura scală naturală)
- `r ≠ 1`: teoria cu două scale — necesită derivare din principii prime

---

## 9) Gaps deschise

1. **Confinement Σ ∈ [0,1]**: cum implementezi mărginirea cuantică fără clip?
   - Candidat A: potențial double-well V = λΣ²(1-Σ)²
   - Candidat B: reprezentare spin S=1/2 (|0⟩, |1⟩) per nod
   - Candidat C: oscilator armonic trunchiat (spațiu Fock finit)

2. **Derivarea ħ_câmp**: din ce principiu apare ħ_câmp și relația sa cu ħ_graf?

3. **Back-reaction câmp-graf**: cum afectează fluctuațiile ⟨(δΣ)²⟩ eigenmodeurile
   grafului? (cuplaj G17 ↔ q-fields)

4. **Predicție modificată Pioneer**: cv_total vs cv_cl → cum se modifică a_lag?

5. **Φ cuantic**: cuantificarea φ (câmp de fază pe cerc) necesită tratament separat
   (teoria câmpului pe S¹, theta-vacuumuri).

---

## 10) Gate experimental asociat

Scriptul `scripts/run_qng_q_fields_v1.py` implementează calculul numeric al:

- K construită pe graful Jaccard oficial (N=280, k=8, seed=3401)
- Diagonalizarea K → {ω_a}
- Fluctuațiile ⟨(δΣ_i)²⟩, ⟨(δΣ_i δχ_i)⟩ per nod
- cv_quantum vs cv_classical (0.405)
- Spectral gap ω_min (criteriu stabilitate cuantică)

Gate-uri Q1–Q5 (exploratorii, nu parte din lane-ul oficial).
