# Pre-Registration: D3 Attack Test v1

**Registered:** 2026-03-05 (înainte de prima rulare)
**Script:** `scripts/run_d3_attack_test_v1.py`
**Seeds:** attack_seed=9999, dataset_seed=3401
**Status:** PRE-REGISTERED — gates și hypothesis declarate înainte de rulare

---

## Motivație

Gate-ul D3 din hardening v4 testează că:
```
cosine_similarity( -g^{-1} · grad(Sigma),  -grad(Sigma) ) >= 0.90  (median)
cosine_similarity( -g^{-1} · grad(Sigma),  -grad(Sigma) ) >= 0.70  (p10)
```

Metrica `g` este derivată din **Hessianul aceluiași câmp Sigma**. Prin construcție,
`g^{-1}` este o transformare liniară a lui `H_Sigma^{-1}`, iar `grad(Sigma)` este
prima derivată a aceluiași câmp. Întrebarea este: este alinierea cos_sim >= 0.90
un rezultat al fizicii QNG, sau un artefact al consistenței interne a oricărui
câmp scalar neted?

---

## Hypothesis

**H0 (null):** D3 trece pentru orice câmp scalar neted, nu doar pentru Sigma QNG.
Dacă H0 e confirmată, D3 nu are putere discriminantă față de câmpuri arbitrare.

**H1 (alternativa):** D3 este specific pentru structura câmpului Sigma QNG.
Câmpurile de control non-Gaussiene sau non-QNG pică D3.

---

## Design Experimental

### Graf
- DS-002: N=280 noduri, k=8 vecini, spread=2.3, seed=3401 (identic cu hardening v4)
- Două variante de graf:
  - `uncoupled`: muchii pur geometrice (distanță euclidiană), fără coupling pe câmp
  - `coupled`: muchii cu coupling pe câmpul de control (identic cu hardening v4)

### Câmpuri de control
| ID | Descriere | Predicție D3 |
|----|-----------|-------------|
| BASELINE_QNG | Sigma original QNG (referință) | PASS |
| C1_RAND_GAUSS | Random Gaussian mixture (4 centre random) | PASS dacă H0 |
| C2_LINEAR | Gradient liniar simplu | PASS dacă H0 |
| C3_SINUS | Câmp sinusoidal periodic | PASS dacă H0 |
| C4_QUADRATIC | Paraboloid quadratic | PASS dacă H0 |
| C5_PURE_NOISE | Zgomot Gaussian pur (nesmoothed) | FAIL (zgomot nu are gradient coerent) |

### Parametri (identici cu hardening v4, nicio modificare)
- Anchor sampling: top-50% + stratified, 72 anchors
- Local chart: 20 noduri, geodesic tangent (2 landmarks)
- Smoothing: Gaussian local, s=s0=1.0
- Metric estimator: v4 (SPD projection + Frobenius norm + anisotropy shrinkage k=0.4)
- D3 threshold: median >= 0.90, p10 >= 0.70
- D4 threshold: shuffled median < 0.55

---

## Criterii de Decizie (pre-declarate)

**CONFIRMAT (H0 corectă):** >= 3 din 4 câmpuri de control C1-C4 trec D3.
**INFIRMAT (H1 corectă):** 0 din 4 câmpuri de control C1-C4 trec D3.
**PARȚIAL:** 1-2 trec — necesită analiză suplimentară.

---

## Ce nu testează acest experiment

Acest test nu infirmă teoria QNG per se. El testează exclusiv dacă **D3 are
putere discriminantă** ca gate de validare. Dacă D3 e non-discriminant, nu
înseamnă că Sigma e greșit — înseamnă că avem nevoie de un gate mai bun care
să distingă Sigma QNG de câmpuri arbitrare.

---

## Anti-tuning policy

Thresholdurile D3/D4 nu vor fi ajustate post-hoc în funcție de rezultate.
Dacă D3 se dovedește non-discriminant, răspunsul corect este să proiectăm
un test mai bun, nu să modificăm thresholdurile existente.
