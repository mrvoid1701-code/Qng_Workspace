# QNG — Next Steps (2026-03-04)

## Prioritate 1 — QM Stage 2 freeze
- [ ] G17b candidate v4: evaluare → switch oficial
- [ ] QM Stage 2 freeze (echivalent "qm stage1 freeze v1")

## Prioritate 2 — Validare cross-dataset G17–G20
- [ ] `python run_all_gates.py --dataset-id DS-003`
- [ ] `python run_all_gates.py --dataset-id DS-006`
- [ ] Toate gate-urile G17–G20 PASS pe cele 3 dataset-uri

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
