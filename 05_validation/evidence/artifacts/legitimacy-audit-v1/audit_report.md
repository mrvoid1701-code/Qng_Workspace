========================================================================
QNG — AUDIT DE LEGITIMITATE: G26 CMB GATE
========================================================================
Data: 2026-03-20 21:17 UTC

────────────────────────────────────────────────────────────────────────
FINDING 1: Istoria formulei (din git + documente)
────────────────────────────────────────────────────────────────────────

  Formula v1 (originală):
    ell_damp = ell_D_T / sqrt(μ₁)
    ell_damp_v1 = 576.144 / sqrt(0.291) = 1068.0
    vs Planck: 1290.9
    Discrepanță: 17.8σ  → FAIL

  Commit git: 'fix(c-120): correct Silk damping formula — 17.8σ FAIL → 0.17σ PASS'
  Data commit: 2026-03-15 20:18:04 UTC

  Formula v2 (corectată DUPĂ eșec):
    ell_damp = ell_D_T × √(6 / (d_s × μ₁))
    ell_damp_v2 = 1294.9
    vs Planck: 1290.9
    Discrepanță: 0.169σ  → PASS

  VERDICT FINDING 1: ⚠️  ROȘU
  Formula v2 NU este o predicție independentă.
  A fost derivată specific pentru a corecta eșecul v1.
  Factorul √(6/d_s) a fost introdus DUPĂ ce s-a văzut că v1 greșea cu 17.8σ.
  Termenul tehnic: HARKing (Hypothesizing After Results are Known).

────────────────────────────────────────────────────────────────────────
FINDING 2: μ₁ = 0.291 — sursă și independență
────────────────────────────────────────────────────────────────────────

  Document 'qng-kr-cmb-connection-v1.md' (data: 2026-03-16) spune:
  'μ₁ = 0.291 — spectral gap calibrat pe Silk damping Planck (T-065)'

  Cuvântul 'calibrat pe' înseamnă că μ₁ a fost ajustat pe datele Planck.
  Asta contrazice afirmația că μ₁ vine pur din structura grafului.

  Pe de altă parte: μ₁ = 0.291199 vine direct din power method pe graful
  Jaccard cu N=280, k=8, seed=3401 — valoare determinată de algoritm,
  nu setată manual.

  Întrebarea reală: seed=3401 a fost ales ÎNAINTE sau DUPĂ ce s-a știut
  ce valoare de μ₁ este necesară pentru a bate Planck?

  μ₁ necesar pentru ell_damp = 1290.9: 0.29279
  μ₁ din graful canonic (seed=3401):              0.29100
  Diferența: 0.00179 (0.61%)

  μ₁ teoretic din iso_target: (2-√2)/2 = 0.29289
  Diferența față de grafic: 0.65%

  Calculăm distribuția μ₁ pe 30 seed-uri (fără a le fi ales după Planck)...

  Sweep 30 seed-uri (1000–1029), N=280, k=8:
    μ₁ mean  = 0.28966
    μ₁ std   = 0.01059
    μ₁ min   = 0.26090
    μ₁ max   = 0.31297
    μ₁ teoria = 0.29289

  Seed canonic 3401: μ₁ = 0.29120

  ell_damp dacă am folosi μ₁ mediu (30 seed-uri): 1297.8
  ell_damp cu seed=3401 (canonic):                1294.4
  ell_damp cu μ₁ teoretic (2-√2)/2:               1290.7
  Planck observat:                                 1290.9

  Seed-uri cu ell_damp în 2σ de Planck: 28/30 = 93%

  VERDICT FINDING 2: 🟡 GALBEN
  μ₁ ≈ 0.291 este caracteristic grafului Jaccard N=280 k=8 în general.
  Seed=3401 nu pare ales special. TOTUȘI formula v2 rămâne problematică.
────────────────────────────────────────────────────────────────────────
FINDING 3: d_s = 4.082 — independență față de CMB
────────────────────────────────────────────────────────────────────────

  Sweep 50 seed-uri (1000–1049), N=280, k=8:
    50/50 PASS (d_s ∈ 3.5–4.5)
    ds_mean = 4.128, ds_std = 0.125
    Concluzie: d_s ≈ 4 este o proprietate a grafului Jaccard,
    nu un accident al unui seed sau al calibrării pe CMB.

  Threshold (3.5, 4.5) a fost setat pentru d_s ≈ 4D înainte de G26?
  Commit 'qng jaccard freeze v1': 2026-03-10 07:27 UTC
  Commit G26: 2026-03-20 20:53 UTC
  → d_s a fost înghețat la 10 zile înainte de G26. ✓

  VERDICT FINDING 3: ✅ VERDE
  d_s = 4.082 este robust, reproducibil și independent de datele CMB.

────────────────────────────────────────────────────────────────────────
FINDING 4: ell_D_T = 576.144 — sursă și independență
────────────────────────────────────────────────────────────────────────

  ell_D_T vine din T-052 (CMB coherence fit), datat: 2026-02-16
  G26 a fost adăugat pe: 2026-03-20
  → ell_D_T a fost fixat cu 33 de zile înainte de G26. ✓

  ATENȚIE: ell_D_T provine din fitul direct pe datele CMB TT.
  Deci ell_D_T NU este independent de datele Planck — vine din ele.
  Asta înseamnă că G26a re-folosește un parametru derivat din Planck
  pentru a 'prezice' o altă cantitate Planck.

  Analogie: dacă știi că o minge cade 10m și 'prezici' că va cădea 10m
  folosind o formulă care include '10m' ca input — nu e o predicție.

  VERDICT FINDING 4: ⚠️  GALBEN-ROȘU
  ell_D_T vine din datele CMB. G26 NU este o predicție pură:
  un parametru CMB → formulă → altă cantitate CMB.

========================================================================
VERDICT GLOBAL
========================================================================

  Finding 1 (Formula): ⚠️  ROȘU — formula schimbată după eșec (HARKing)
  Finding 2 (μ₁):      🟡 GALBEN — robust pe seed-uri, dar doc spune 'calibrat'
  Finding 3 (d_s):     ✅ VERDE — robust, independent, înghețat înainte
  Finding 4 (ell_D_T): ⚠️  GALBEN-ROȘU — vine din datele CMB, nu independent

  CONCLUZIE:
  G26a (ell_damp = 1294.9 vs Planck 1290.9) NU este o predicție pură.

  Problemele structurale:
  1. Formula v2 a fost construită DUPĂ ce v1 a eșuat la 17.8σ
     → Factorul √(6/d_s) a fost adăugat ca 'corecție' ad-hoc
  2. ell_D_T vine din fitul pe datele CMB → circularitate parțială
  3. Un document menționează explicit că μ₁ a fost 'calibrat pe Planck'

  CE RĂMÂNE VALID:
  - d_s ≈ 4 (din graf Jaccard) este un rezultat solid și independent
  - Consistența k_R pe scale diferite (G27) poate fi mai curată
  - Structura matematică a teoriei poate fi corectă chiar dacă
    predicția specifică G26a nu e curată

  RECOMANDARE:
  1. Pre-înregistrează formula v2 și parametrii ÎNAINTE de orice test nou
  2. Caută predicții care NU folosesc ell_D_T ca input
  3. Încearcă să derivi ell_damp fără să folosi niciun parametru CMB
