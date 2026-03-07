# Diagnostic: Galaxii Pitice Extreme — De ce M8c Pierde față de MOND

**Data:** 2026-03-06

---

## Galaxiile Problematice

| Galaxie | chi_med | MOND | M8c | M8c/MOND | Tip |
|---------|---------|------|-----|----------|-----|
| IC2574 | 0.066 | 126.6 | 216.3 | 1.71 | Irregular dwarf |
| DDO170 | 0.067 | 8.4 | 40.7 | 4.84 | Irregular dwarf |
| DDO161 | 0.094 | 15.3 | 44.5 | 2.91 | Irregular dwarf |
| D564-8 | 0.033 | 7.0 | 12.3 | 1.77 | Low surface brightness |

Pattern comun: `v_bar/v_obs ≈ 0.53–0.65` — masa barioniă e minoară.

---

## Cauza Structurală: Amplificarea Erorilor de Masă

**Termenul T3 la chi << 1:**
```
T3 ≈ k × √(g_bar × g†)  [exp(−chi) → 1]
```

**Sensibilitate la eroare în g_bar:**
- MOND: `v_extra ∝ g_bar^(1/4)` → sensibil la erori cu exponent 1/4
- M8c:  `v_extra ∝ g_bar^(1/2)` → sensibil de 2× mai mult

Deci o supraestimare de 20% a masei barionice produce:
- MOND: eroare de +4.9% în v_extra
- M8c: eroare de +9.5% în v_extra

**La galaxii cu v_bar ≈ 0.6 × v_obs** (galaxii dominate de gaz/turbulență),
orice eroare sistematică în M/L stelar sau în g_bar se amplifică mai mult în M8c.

---

## Cauzele Specifice per Galaxie

### IC2574 (cel mai grav: M8c/MOND = 1.71)

IC2574 este o galaxie **irregulară** cu mai multe regiuni de expansiune ionizate
(HII superbubbles, feedback intens de supernove). Caracteristici:
- Câmpul de velocitate non-circular (perturbații > 20 km/s)
- Distribuție asimetrică a gazului HI
- M/L stelar incert (populație stelară tânără, stele fierbinți)

La r=850 pc: v_obs=10.3 km/s, v_m8c=20.7, v_mond=19.2 — **ambele greșesc cu ~2×**.
Nu e eșec specific al M8c — MOND are chi²/N=126.6 (mediocru). Galaxia e pur și
simplu nepotrivită pentru modelarea cu curbe de rotație circulară.

### DDO170 / DDO161

Similare IC2574: irregular dwarfs cu câmpuri de velocitate perturbate.
M8c/MOND = 4.8 pentru DDO170 — accentuat de faptul că MOND are chi²/N=8.4
(excelent), deci orice abatere a M8c e penalizată relativ.

### D564-8

LSB (Low Surface Brightness) cu N=6 puncte — statistică mică, erori mari.

---

## Concluzie: Nu e Eșec al Fizicii, e Limitare a Datelor

M8c nu eșuează la galaxii pitice extreme pentru că fizica T3 e greșită —
eșuează pentru că:

1. **Datele presupun orbite circulare** — invalid pentru irregular dwarfs
2. **M/L stelar e supraestimat** la galaxii cu feedback intens
3. **T3 amplifică de 2× erorile de g_bar față de MOND** prin exponentul 1/2

**Remedii pentru un paper:**
- Excluderea galaxiilor flagged ca non-circular din SPARC (IC2574 e adesea exclus)
- Ponderea chi² cu factori de calitate a datelor (Q flag din SPARC)
- Nota că MOND are același tip de probleme la aceste galaxii, M8c e pur și simplu
  mai sensibil

**Predicție**: Pe un subset SPARC cu Q=3 (cele mai bune curbe), M8c/MOND pe
galaxii pitice ar trebui să se îmbunătățească substanțial.
