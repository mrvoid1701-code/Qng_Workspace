# QNG — Next Steps (2026-03-07)

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

## Prioritate 4 — Bulletproofing (după paper draft)
- [ ] Cross-seed sweep larg pe G17a (spectral gap sensibil la seed)
- [ ] Justificare analitică lower bound G18d (d_s ≥ 1)
- [ ] G21 candidat: consistență termodinamică (S ≥ 0, T > 0 global)

## Ordine recomandată
QM Stage 2 freeze → Cross-dataset → Paper draft → Bulletproofing pe feedback
