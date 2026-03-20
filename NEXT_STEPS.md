# QNG — Next Steps (2026-03-09)

## Prioritate 1 — QM Stage 2 freeze
- [x] G17b candidate v4: evaluare → switch oficial (done 2026-03-04, official-v14 activ)
- [ ] QM Stage 2 freeze (prereg rulează, ~acasă)

## Prioritate 2 — Validare cross-dataset G17–G20 ✓ DONE (2026-03-07)
- [x] `python run_all_gates.py --dataset-id DS-003` — 10/11 (G15 FAIL, G17-G20 ✓)
- [x] `python run_all_gates.py --dataset-id DS-006` — 11/11 ALL PASS
- [x] Toate gate-urile G17–G20 PASS pe cele 3 dataset-uri
- See: `docs/CROSS_DATASET_VALIDATION_V1.md`
- Known: DS-003 G15b Shapiro 1.944 < 2.0 (structural, GR gate only, nu blochează QM)

## Prioritate 3 — Primul paper (arXiv preprint)
Structură:
- §1 Intro: emergent spacetime din grafuri
- §2 Metrică ADM (G10–G12)
- §3 Câmp + conservare + PPN (G13–G15)
- §4 Principiu variațional (G16)
- §5 Cuantizare canonică + informație cuantică (G17–G18)
- §6 Temperatura Unruh + back-reaction semiclasic (G19–G20)
- §7 Stabilitate + validare multi-dataset
- §8 Concluzii: loop-ul GR↔QM închis pe grafuri discrete

## Prioritate 4 — Integrare Graf Informational (2026-03-08, NOU)

**Descoperire:** graful k-NN 2D impune artificial d_s ≈ 1.35 (artifact embedding).
**Solutie:** Jaccard Informational Graph + Lazy Random Walk → d_s = 4.082 ≈ 4.0.
**Documentatie:** `01_notes/coordfree-graph-discovery-v1.md`
**G18d v2:** `scripts/run_qng_g18d_v2.py` — toate G18 PASS cu d_s=4.082.

Plan integrare (in ordine):
- [x] G18d v2: Jaccard + Lazy RW implementat si testat
- [ ] Paper section: §X Emergent 4D Dimensionality (`06_writing/paper-coordfree-4d-v1.md`)
- [x] G17: re-rulare pe graf Jaccard → 4/4 PASS (2026-03-09, μ₁=0.291)
- [x] G10-G12 (ADM, Ricci, Schwarzschild): PASS pe Jaccard (2026-03-09)
- [x] G13-G15 (conservare, PPN, Shapiro): PASS pe Jaccard, G15b=2.51>2.0 ✓
- [x] G16 (actiune variationala): PASS pe Jaccard — frac_neg_hess=1.000 (perect!)
- [x] run_all_gates.py: grup "jaccard" adaugat → 3/3 PASS (2026-03-09)

**Risc inițial:** GR gates calibrate pe grafuri 2D — re-calibrare probabila.
**REZULTAT:** 7/7 PASS fără re-calibrare! Teoria e robustă față de tipul grafului.
**Strategie:** mai intai G17-G18 (robuste spectral), apoi G10-G16. ✓ DONE.

## Prioritate 5 — Bulletproofing (după paper draft)
- [x] Cross-seed sweep d_s: 50/50 PASS (100%), mean=4.128±0.125, r²=0.997 (2026-03-09)
- [x] Sweep parametri (N×k): diagramă de fază completă (2026-03-09)
  - 28 celule (7 N × 4 k), mediat pe 3 seed-uri, r²>0.982 în toate
  - k=8: 6/7 PASS (N≥150); k=6 subsaturat (d_s<3.5); k≥10 suprasaturat (d_s>4.5)
  - Canonical (N=280, k=8) bine centrat în banda d_s∈(3.5,4.5)
  - Notă: `01_notes/jaccard-phase-diagram-v1.md`
- [x] Justificare analitică G18d: de ce Jaccard → d_s=4 (conexiune cu CDT/LQG) — DONE (2026-03-20, `03_math/derivations/qng-jaccard-ds4-analytical-v1.md`)
- [x] G21 candidat: consistență termodinamică (S ≥ 0, T > 0 global) — 4/4 PASS (2026-03-09)
- [x] G19/G20 v2 pe Jaccard: PASS (2026-03-09)
  - G19: `run_qng_g19_jaccard_v1.py` — 4/4 PASS (G19d cu BFS hop distance)
  - G20: `run_qng_g20_jaccard_v1.py` — 4/4 PASS (back-reaction, E_0 conservat la 3e-16)
  - G21: `run_qng_g21_thermo_v1.py` — 4/4 PASS (S>0, C_V>0, F=U-TS, S(2T)/S(T)=5542, 2026-03-09)
  - `scripts/run_all.py --group jaccard` → **6/6 PASS** (G10-G21 complet pe Jaccard, 22.9s)

## Ordine recomandată
QM Stage 2 freeze → Paper draft (cu sectiune 4D) → Integrare graf Jaccard → Bulletproofing

---

## STATUS CURENT (2026-03-09)

### Ce e gata (toate PASS)
- GR gates G10–G16: 600/600 primary + 1500/1500 attack + 400/400 holdout (oficial, frozen)
- QM gates G17–G21: G17-G20 frozen (2500/2500); G21 nou adăugat (4/4 PASS pe Jaccard)
- Stabilitate: convergence v6 oficial, dual-channel, regression guard verde
- Cross-dataset: DS-002 11/11 ✓, DS-003 10/11 ✓ (G15 structural, non-blocking), DS-006 11/11 ✓
- d_s = 4.082 emergent din Jaccard graph (G18d v2 PASS)

### Ce urmează imediat
1. **[DONE ✓]** `run_gr_gates_jaccard_v1.py` → 7/7 PASS pe Jaccard (2026-03-09)
2. **[DONE ✓]** `run_qng_g17_v2.py` pe Jaccard → 4/4 PASS, μ₁=0.291 (2026-03-09)
3. **[DONE ✓]** `run_all.py --group jaccard` → 3/3 PASS (G10-G18, 2026-03-09)
4. **[DONE ✓]** Multi-seed sweep d_s: 50/50 PASS (100%), mean=4.128±0.125 (2026-03-09)
5. **[DONE ✓]** G19/G20 pe Jaccard → 5/5 PASS (G10-G20 complet, 2026-03-09)
6. **[URMĂTOR]** Paper draft — full QNG paper (toate gate-urile PASS pe Jaccard)

### Pașii care BLOCHEAZĂ paper-ul
- GR gates trebuie să treacă pe Jaccard (altfel paper-ul nu poate afirma că teoria e independentă de embedding)
- Dacă GR fail → re-calibrare thresholds + governance commit necesar
