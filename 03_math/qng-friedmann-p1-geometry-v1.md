# QNG: Geometrie FRW — De ce R_Forman ≠ 6H² și Ecuația Raychaudhuri QNG

**Status**: DERIVARE COMPLETĂ (ecuație Raychaudhuri QNG), + DIAGNOSTIC gap H² = (8πG/3)ρ
**Versiune**: v1
**Data**: 2026-03-22
**Dependințe**: qng-friedmann-v1.md §1.2-1.3, qng-sigma-dynamics-v1.md §7, qng-core-emergent-metric-v1.md
**Completează**: P-F1 din qng-friedmann-v1.md §5 (gap identificat ca "legătura R→H")

---

## 1. Problema: Ce Este P-F1?

qng-friedmann-v1.md §5 identifică gap-ul:

> "Ce lipsește: conexiunea explicită R_QNG(t) = f(H(t), ä(t)/a(t))"

Scopul P-F1: derivăm **ecuația Raychaudhuri QNG** (analogul ecuației de accelerație din GR)
și clarificăm de ce R_Forman nu este obiectul geometric potrivit.

---

## 2. De ce Forman-Ricci NU este 6H²

### 2.1 Curvatura Forman-Ricci pentru graf ER omogen

Pentru un graf Erdős-Rényi cu N_s noduri, grad mediu k și fără triunghiuri (t=0):

```
<R_F>(t) = 4 - 2k + 2k²/N_s(t)
```

Termenul structural: `D(t) ≡ 2k²/N_s(t)`

### 2.2 Evoluția în expansiune

Cu N_s(t) = N_s(t₀) exp(3∫H dt):

```
dD/dt = -2k² Ṅ_s / N_s² = -3H * D(t)
D(t) = D₀ * exp(-3∫H dt) = D₀/a³(t)
```

Deci:

```
<R_F>(t) = (4 - 2k) + D₀/a³(t)
```

Comportament:
- a(t) → ∞: `<R_F> → (4-2k) = const`   [de Sitter: curvatura tinde la constantă]
- a(t) → 0: `<R_F> → ∞`                  [Big Bang: curvatura diverge]

**Concluzie**: R_Forman se comportă ca `D₀/a³ ~ ρ_materie`, NU ca `6H²`.

### 2.3 Ce este 6H² în GR

Scalarul Ricci pentru FRW plat:

```
R_GR = 6 (ä/a + H²) = 6(Ḣ + 2H²)
```

Aceasta implică **derivate temporale ale metricii** (curbura extrinsecă), nu curbura
intrinsecă a hipersuprafețelor spațiale (care e zero în FRW plat).

**Analogia corectă:**
- R_Forman = curbura intrinsecă a grafului = 0 în FRW plat (K=0)
- Curbura extrinsecă K_ij ~ H δ_ij = vine din **evoluția temporală a metricii**

---

## 3. Ecuația Raychaudhuri QNG — Derivare Directă

Avem două ecuații de bază:

### 3.1 Metrica FRW din metric-lock-v5

În limita izotropă (câmp uniform):

```
g_ij(t) = (1 - 2Σ₀(t)) δ_ij    →    a_met²(t) = 1 - 2Σ₀(t)
```

### 3.2 EOM-Σ temporal (qng-sigma-dynamics-v1.md §7, extensia d'Alembertian)

```
□_g Σ = (-∂²_t + Δ_g)Σ = α ρ
```

În limita omogenă (∇Σ₀ = 0):

```
-Σ̈₀(t) = α ρ₀(t)
→  Σ̈₀(t) = -α ρ₀(t)                                         [EOM-Σ-cosm]
```

### 3.3 Parametrul Hubble din a_met

```
H = ȧ/a = d/dt[√(1-2Σ₀)] / √(1-2Σ₀)
        = [-Σ̇₀/√(1-2Σ₀)] / √(1-2Σ₀)
        = -Σ̇₀/(1-2Σ₀)
        = -Σ̇₀/a²
```

Deci:

```
Σ̇₀ = -H a²    →    Σ̇₀ = -H(1 - 2Σ₀)                        [Σ-H-rel]
```

**Semnul fizic**: expansiune (H > 0) implică Σ̇₀ < 0 — câmpul de stabilitate
scade cu expansiunea universului. ✓

### 3.4 Derivarea Ḣ

Diferențiind [Σ-H-rel]:

```
Σ̈₀ = -Ḣ(1-2Σ₀) - H*(-2Σ̇₀) = -Ḣ a² + 2HΣ̇₀ = -Ḣ a² + 2H(-Ha²) = -Ḣ a² - 2H²a²
```

Deci:

```
Σ̈₀ = -a²(Ḣ + 2H²)
```

### 3.5 Substituție în EOM-Σ-cosm

```
-a²(Ḣ + 2H²) = -α ρ₀
```

**Ecuația Raychaudhuri QNG:**

```
╔══════════════════════════════════════════════════════════╗
║                                                           ║
║   Ḣ + 2H² = α ρ₀ / a²(t)                               ║
║                                                           ║
║   unde α = 4πG_eff   și   a²(t) = 1 - 2Σ₀(t)          ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
```

**Sau echivalent** (înlocuind a² = 1-2Σ₀):

```
Ḣ + 2H² = α ρ₀ / (1 - 2Σ₀(t))
```

---

## 4. Comparație cu GR

### 4.1 GR: Ecuația Raychaudhuri (accelerație)

```
ä/a = Ḣ + H² = -(4πG/3)(ρ + 3p)     [GR standard]
```

### 4.2 QNG vs GR

| Termen | GR | QNG |
|--------|-----|-----|
| Coeficient H² în LHS | 1 | 2 |
| Semn RHS pentru materie (p=0) | negativ (decelerare) | pozitiv (accelerare!) |
| Dependență de a | niciuna | divide prin a² |

**Diferența fundamentală**: GR dă decelerare pentru materie; QNG dă accelerare pentru
materie când a < 1 (univers mic). Aceasta diferă de observație.

### 4.3 Sursa discrepanței — analiza termenilor

Din [Σ-H-rel]: Σ̇₀ = -Ha²

Derivând din nou: Σ̈₀ = -(Ḣa² + 2Hȧa) = -(Ḣ + 2H²)a²

Comparând cu GR Raychaudhuri scris în termenii de câmp scalar σ (analogul lui Σ):
- GR: σ̈ + 3Hσ̇ + V'(σ) = 0 → Ḣ + H² = -(4πG/3)(σ̇² - V(σ))

Diferența: termenul 3Hσ̇ din GR (amortizare Hubble pentru câmpul scalar) lipșeste
din QNG deoarece metrica QNG a_met = √(1-2Σ) nu este o metrică FRW standard.

---

## 5. Ce Lipsește pentru H² = (8πG/3)ρ

### 5.1 Ce am derivat

Ecuația Raychaudhuri QNG: `Ḣ + 2H² = αρ₀/a²` (curba de accelerație)

### 5.2 Ce este Friedmann 1

Friedmann 1: `H² = (8πG/3)ρ` (constraint de energie)

Aceasta este **o ecuație independentă** de Raychaudhuri. În GR vine din componenta
G₀₀ = 8πG T₀₀ a ecuațiilor Einstein, care este o CONSTRÂNGERE HAMILTONIANA, nu o
ecuație de evoluție.

### 5.3 De ce QNG nu o derivă automat

Acțiunea de stabilitate QNG (qng-stability-action-v1.md) nu conține un termen cinetic
explicit `(Σ̇)²` sau `(ȧ)²`. Deci nu există Lagrangian „gravitațional" din care să
rezulte o constrângere Hamiltoniană cu H² pe stânga.

Comparativ, în GR:
```
S_EH = ∫ √(-g) R d⁴x  →  conține (ȧ)² în FRW  →  H² apare în ecuațiile de mișcare
```

În QNG:
```
S_QNG = Σ_t Σ_i L_i,t    (fără termen (Σ̇)²)  →  H² NU apare direct
```

### 5.4 Două rute posibile pentru P-F1 complet

**Ruta A: Energie totală de câmp Σ**

Adăugând un termen cinetic la acțiunea de stabilitate:
```
L_i,t → L_i,t + (k_kin/2)(Σ̇_i)²
```
Constrângerea Hamiltonică (∂S/∂N = 0 unde N = lapse):
```
N_s * [(k_kin/2)Σ̇₀² - V(Σ₀)] = 0
```
Dacă V(Σ₀) = (k_kin/2) Σ̇₀² → constrângere trivială (H² nu apare explicit).
**Nu funcționează direct.**

**Ruta B: Constrângere Volumetrică**

Consistența între a_vol = (N_s/N_{s,0})^{1/3} și a_met = √(1-2Σ₀):
```
N_s/N_{s,0} = (1-2Σ₀)^{3/2} = a_met³
```
Diferențiind:
```
(1/N_s)dN_s/dt = (3/2) * (-2Σ̇₀)/(1-2Σ₀) = -3Σ̇₀/a² = 3H
```
Aceasta e consistent (definite H din ambele definiții). Dar tot nu dă H² = (8πG/3)ρ
fără informație suplimentară despre relația ρ-H.

**Ruta C: Identificarea cu Spectrul Jaccard**

Din qng-friedmann-v1.md §2.5:
```
ρ_QNG = (1/(2N_s V₀)) Σ_k √λ_k
```
Și H = (1/3)Ṅ_s/N_s. Dacă spectrul Jaccard λ_k ~ H^n pentru un anumit n,
atunci ρ ~ H^n → H² ~ ρ^{2/n}.

Pentru H² = (8πG/3)ρ: n=2, deci λ_k ~ H².

**Ruta D: Analogia ADM Discretă (cel mai promițătoare)**

În ADM, constrângerea Hamiltonică vine din invarianța la reparametrizare temporală.
În QNG discret, aceasta ar fi invarianța la permutarea pașilor de timp → constrângere
pe energia totală pe fiecare pas.

```
E_total(t) = Σ_i [V(Σ_i) + T(Σ̇_i)] = 0   (constrângere Hamiltonică QNG)
```

Dacă V(Σ₀) = -(3/8πG_eff) H² a³ și T(Σ̇₀) = (3/8πG_eff) H² a³ + ρ a³:
→ constrângere: 0 = ρ - (3/8πG_eff) H² → H² = (8πG/3)ρ

Aceasta ar funcționa DAR necesită identificarea explicită a termenilor energetici
din acțiunea QNG cu termenii ADM din GR. Aceasta este practic derivarea limitei
continui QNG → GR, care este un task major separat.

---

## 6. Ce Predicții Face QNG Diferit de GR

Din ecuația Raychaudhuri QNG: Ḣ + 2H² = αρ/a²

**Corecție față de GR** (în limita a ≈ 1, Σ₀ ≈ 0):

```
ä/a = Ḣ + H² = (αρ/a² - 2H²) + H² = αρ/a² - H²
```

Vs GR: ä/a = -(4πG/3)(ρ + 3p)

Diferența: QNG = GR_corrected + (αρ/a² + (4πG/3)(ρ+3p) - H²)

Cu α = 4πG și a ≈ 1 (epocă actuală):
```
δ(ä/a) ≈ 4πGρ + (4πG/3)ρ - H² = (16πG/3)ρ - H²
```

Pentru Ω_m ~ 0.3 și H₀² = (8πG/3)ρ_crit → H₀² ≈ (8πG/3)ρ:
```
ρ ≈ 0.3 * 3H₀²/(8πG)
δ(ä/a) ≈ (16πG/3)*0.3*(3H₀²/(8πG)) - H₀² = 0.6H₀² - H₀² = -0.4H₀²
```

**Corecție QNG față de GR**: O termen suplimentar -0.4H₀² în ä/a în epoca actuală.
Aceasta este o predicție testabilă (diferă de GR cu ~40% în accelerație pentru Ω_m=0.3).

---

## 7. Rezumat și Status P-F1

| Obiectiv | Status | Detalii |
|----------|--------|---------|
| R_Forman ≠ 6H² | DOVEDIT | R_F → const, nu H² |
| Obiect geometric corect | IDENTIFICAT | Curbura extrinsecă K ~ Σ̇₀/a² ~ H |
| Ecuația Raychaudhuri QNG | DERIVAT | Ḣ + 2H² = αρ/a² |
| Friedmann H²=(8πG/3)ρ | NEDERIVATD | Necesită constrângere Hamiltonică (Ruta D) |
| Diferența QNG vs GR | CALCULAT | Corecție ~40% în ä/a la parametrii curenti |

**Concluzie pentru P-F1**: Ecuația de accelerație (Raychaudhuri) este derivată complet.
Ecuația de constraint energetic (Friedmann 1) necesită extinderea ADM discretă a QNG —
un task major care depășește scopul acestui document.

**Implicație pentru Ω_Λ**: Rămâne neschimbată. Ω_Λ ~ 1/N este o identitate spectrală
care nu depinde de care formă a Friedmann e corectă.

---

*Documente conexe:*
- `qng-friedmann-ns-dynamics-v1.md` — dinamica N_s(t), Friedmann Forma I (H-Σ)
- `qng-friedmann-v1.md` — setup cosmologic, proto-Friedmann
- `03_math/derivations/qng-sigma-dynamics-v1.md` — EOM-Σ (sursa EOM-Σ-cosm)
- `03_math/derivations/qng-core-emergent-metric-v1.md` — metrica emergentă din distanță graf
