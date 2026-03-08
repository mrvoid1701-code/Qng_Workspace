# QNG — Next Steps (2026-03-08)

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
- [ ] G17: re-rulare pe graf Jaccard, verificare gap spectral
- [ ] G10-G12 (ADM, Ricci, Schwarzschild): re-validare pe noul graf
- [ ] G13-G15 (conservare, PPN, Shapiro): re-validare
- [ ] G16 (actiune variationala): re-validare
- [ ] run_all_gates.py: switch oficial la graf Jaccard + lazy RW

**Risc:** GR gates (G10-G16) calibrate pe grafuri 2D — re-calibrare probabila.
**Strategie:** mai intai G17-G18 (robuste spectral), apoi G10-G16.

## Prioritate 5 — Bulletproofing (după paper draft)
- [ ] Cross-seed sweep larg pe G17a (spectral gap sensibil la seed)
- [ ] Justificare analitică G18d: d_s ∈ (3.5, 4.5) vs (1.0, 3.5) vechi
- [ ] Stabilitate Jaccard: sweep pe k_init, k_conn, seed → confirmare robustete d_s
- [ ] G21 candidat: consistență termodinamică (S ≥ 0, T > 0 global)

## Ordine recomandată
QM Stage 2 freeze → Paper draft (cu sectiune 4D) → Integrare graf Jaccard → Bulletproofing
