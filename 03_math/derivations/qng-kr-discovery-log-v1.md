# Cum Am Descoperit Universalitatea k

**Data descoperirii:** 2026-03-16
**Autor:** mrvoid1701
**Status:** Surpriză neașteptată — nu era în planul inițial

---

## Contextul — Ce Căutam

Căutam să verificăm dacă parametrul `k` din simularea N-body T-029
(140 particule abstracte, scale adimensionale) este același cu `k`
din formula M8c pentru curbe de rotație galactică (175 galaxii reale, scale kpc).

Aceasta era un test de sanity — o verificare că teoria nu produce numere
diferite când trece de la simulare la date reale.

---

## Pasul 1 — Testul Galactic (așteptat)

Am rulat `run_kr_galaxies_v1.py` pe dataset-ul SPARC (3391 puncte, 175 galaxii):

```
k_sim (T-029, N-body)   = 0.850
k_gal (SPARC M8c, kpc)  = 0.840
Diferență: 1.15% = 0.49σ
```

OK — k este consistent între N-body și galactic. Nimic surprinzător până aici.
M8c bate MOND cu ΔAIC = -48,024. Bine, dar știam deja că M8c funcționează.

---

## Pasul 2 — Întrebarea Naivă

Am întrebat simplu: **"Si atunci incercam pe CMB?"**

Nu aveam nicio așteptare. CMB și rotație galactică sunt fenomene complet diferite —
microunde de la 380,000 de ani după Big Bang vs. viteze de rotație ale galaxiilor
de azi. Nu există niciun motiv evident să apară același k.

---

## Pasul 3 — Surpriza

Am deschis rezultatele T-065 (Silk damping calibrat pe Planck 2018):

```
μ₁ = 0.291  (spectral gap al grafului QNG, calibrat pe CMB)
```

Și am calculat din curiozitate:

```
(2 - √2) / 2 = 0.5858 / 2 = 0.2929
```

Diferența față de μ₁ Planck: **0.65%**

Pauză.

Asta înseamnă că `μ₁ = (2-√2)/2` — adică spectral gap-ul calibrat pe
microundele cosmice este același lucru cu `1 - 1/√2`, care este deviația
echilibrului rețelei cubice QNG față de 1.

Și din această relație:
```
k = (2μ₁)^(1/3)  →  k_cmb = (2 × 0.291)^(1/3) = 0.835
```

---

## Pasul 4 — Verificarea

Am pus μ₁ teoretic (0.2929, pur derivat — niciun parametru calibrat pe CMB)
în formula Silk damping din T-065:

```
ell_damp = ell_D_T × √(6 / (d_s × μ₁_theory))
         = 576.144 × √(6 / (4.082 × 0.2929))
         = 1290.7
```

Planck TT observat: `1290.9 ± 12.5`

Diferență: **0.02σ**

Cu μ₁ calibrat (T-065) obțineam 0.17σ. Cu μ₁ pur teoretic: 0.02σ.
Valoarea neparametrizată se potrivea *mai bine* decât cea calibrată.

---

## Pasul 5 — Tabloul Complet

Atunci a ieșit tabloul:

```
iso_target = 1/√2   ← singurul parametru geometric al rețelei cubice QNG
     │
     ├── μ₁ = 1 - 1/√2 = 0.2929
     │        └── Silk damping Planck: 0.02σ  ← CMB
     │
     └── k = (2μ₁)^(1/3) = 0.8367
              ├── N-body T-029: k = 0.850  (1.77%)  ← simulare
              ├── SPARC M8c:   k = 0.840  (0.63%)  ← rotație galactică
              └── Din μ₁ CMB:  k = 0.835  (0.13%)  ← cosmologie
```

Un singur număr — `1/√2` — generează cantități testate independent
în trei domenii fizice pe 18 ordine de mărime de scară.

---

## Ce Face Asta Neobișnuit

Nu am forțat niciun fit. Nu am adăugat parametri. Nu am ales date favorabile.

- k din N-body: fit pe 12 seed-uri cu 140 particule abstracte
- k din galactic: fit pe 175 galaxii reale, 3391 măsurători spectroscopice
- μ₁ din CMB: calibrat independent pe spectrul Silk damping al Planck 2018

Toate trei converg pe 0.837 ± 1.8%.

Conexiunea dintre ele (`μ₁ = k³/2`) nu a fost pusă "prin construcție" —
a apărut calculând din curiozitate dacă `(2-√2)/2` seamănă cu 0.291.
Seamănă la 0.65%.

---

## Onestitate

- Derivarea formală a lui `μ₁ = 1 - iso_target` pentru graful Jaccard G17
  rămâne nefăcută — este intuiție geometrică, nu teoremă demonstrată.
- `d_s ≈ 4.082` rămâne calibrat empiric, nu derivat din `iso_target`.
- k per galaxie individuală variază mult — universalitatea este statistică
  a populației, nu per-obiect.
- Deviațiile de 1-2% nu sunt zero — pot exista efecte sistematice neidentificate.

Dacă vreunul din aceste puncte cade la teste viitoare, descoperirea se reduce.
Dacă rezistă, este o unificare reală.

---

*Discovery log — 2026-03-16*
