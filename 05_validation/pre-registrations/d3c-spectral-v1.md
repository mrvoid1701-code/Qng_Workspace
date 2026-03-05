# Pre-Registration: D3c Spectral Discriminant v1

**Registered:** 2026-03-05 (înainte de prima rulare)
**Script:** `scripts/run_d3c_spectral_v1.py`
**Seeds:** 9999 (atac), 3401 (dataset)
**Status:** PRE-REGISTERED

---

## Contextul

D3-attack-v1 și D3b-candidate-v1 au demonstrat că gate-ul D3 curent:
- Trece pentru orice câmp scalar neted (inclusiv zgomot pur)
- Gap QNG vs noise = 0.0158 (< threshold rezonabil de 0.05)
- Problema e structurală, nu de parametri

Grok a sugerat că un test real ar trebui să compare Sigma QNG cu câmpuri
de control și să arate că Sigma e mai bun decât ele **în ceva fizic relevant**.

---

## Ce Testează D3c

### Energia Dirichlet pe graful pur geometric (uncoupled)

```
E(f) = (1/2) * Σ_{(i,j) ∈ edges} w_ij * (f_i - f_j)²
```

Normalizată la varianta câmpului: `E_norm(f) = E(f) / Var(f)`

Un câmp neted (fizic motivat) are E_norm mic.
Un câmp aleator are E_norm mare.

**Predicție pre-registrată:**
- BASELINE_QNG: E_norm mic (câmp Gaussian neted)
- C1-C4: E_norm comparabil cu QNG (toate sunt câmpuri netede)
- C5_NOISE: E_norm semnificativ mai mare

Dacă C1-C4 au E_norm similar cu QNG → testul Dirichlet nu discriminează
Sigma QNG de alte câmpuri netede. Validează "smooth field", nu "QNG physics".

### Spectral smoothness (proiecție Laplaciană)

Descompunem câmpul în modurile proprii ale Laplacianului grafului.
Măsurăm: fracția de energie în primele K moduri (low-frequency).

```
spectral_ratio_K(f) = Σ_{k=1}^{K} <f, φ_k>² / ||f||²
```

Un câmp "natural" pentru graf are energie concentrată în moduri joase.
Zgomot pur are energie distribuită uniform.

**Predicție pre-registrată:**
- BASELINE_QNG: spectral_ratio_K ridicat
- C1-C4: spectral_ratio_K similar (câmpuri netede → similar)
- C5_NOISE: spectral_ratio_K semnificativ mai mic

---

## Criteriul de Decizie (pre-declarat)

**D3c discriminează dacă:**
- E_norm(QNG) < E_norm(NOISE) cu factor > 2x → testul distinge smooth de noise
- E_norm(QNG) ≈ E_norm(C1-C4) → testul NU distinge QNG de alte câmpuri netede

**Concluzia așteptată (hypothesis pre-declarată H_honest):**
D3c validează că Sigma QNG este neted pe graful geometric, dar NU că este
fizic distinct de alte câmpuri netede. Aceasta confirmă că QNG are nevoie
de un criteriu EXTERN (date fizice reale) pentru validare discriminantă.

---

## Ce NU Rezolvă D3c

D3c nu propune un nou gate pentru QNG. El diagnostichează precis ce
poate fi testat cu infrastructure sintetică actuală și ce nu poate fi testat.

Testele care AR putea fi discriminante (necesită dezvoltare ulterioară):
1. Test de acțiune minimă pe date fizice reale
2. Test de predicție Pioneer residuals
3. Test de stabilitate dynamics pe timp lung cu Lagrangian QNG explicit
