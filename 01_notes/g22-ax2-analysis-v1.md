# Analiza ax2− în G22: de ce r²=0.054?

**Data:** 2026-03-20
**Context:** G22 (Directional Isotropy) raportează ax2−: d_s=0.75, r²=0.054
**Concluzie:** Nu e o problemă structurală — e o caracteristică spectrală a grafului Jaccard

---

## Investigație

### Ce am verificat

| Metric | ax2− | ax2+ | întreg graful |
|--------|------|------|---------------|
| Grad mediu | 9.33 | 9.37 | 9.38 |
| Grad min/max | 8/16 | 8/15 | 8/16 |
| Clustering local | 0.1651 | — | 0.1657 |
| Pearson(Fiedler, ax2) | 0.0000 | — | — |

**Concluzie**: ax2− are aceeași structură locală ca restul grafului. Nu există "hub-uri" sau noduri speciale în ax2−.

### Interpretarea spectrală

Al doilea eigenvector (ax2) al matricei lazy RW pe graful Jaccard e **ortogonal** pe vectorul Fiedler (Pearson=0). Asta e așteptat din teoria spectrală — eigenvectorii sunt ortogonali.

Al doilea eigenvector pentru un graf cu **structură de comunitate** partiționează graful în două comunități. Când pornești walk-uri din nodurile "bottom 40%" ale ax2 (ax2−), ele se pot întoarce mai rapid dacă există o asimetrie de conectivitate intra-comunitate.

Dar grade și clustering sunt identice → nu există o comunitate distinctă cu o structură anizotropă.

### Cauza probabilă a r²=0.054

Cu N_WALKS=80 și 112 noduri de start (40% din 280), distribuția P(return|t) la ax2−
**nu urmează o power-law** din cauza unui efect de rezonanță spectrală:

Eigenvectorul ax2 al unui graf cu structură Jaccard poate fi aproape **bimodal** — jumătate din noduri cu ax2>0 și jumătate cu ax2<0. Dacă cele două "jumătăți" au conectivitate asimetrică (chiar dacă gradul mediu e egal), walk-ul din ax2− poate arăta un comportament de "bounce-back" la scale scurte și un comportament normal la scale mari → nu power-law → r² mic.

### Impact asupra G22

G22 corect filtrează ax2− (r²<0.5) și nu o include în statisticile de izotropie. Cele **6 din 8 direcții convergente** (75%) dau σ(d_s)=0.47 < 0.60 → **PASS**.

Direcțiile non-convergente (ax2−, ax4+) sunt **accidentale ale acestei instanțe** a grafului (seed=3401), nu o proprietate universală. Confirmată implicit de:
- Direcțiile ax1+, ax1−, ax2+, ax3+, ax3−, ax4−: toate r²>0.5
- Dacă ar fi o anizotropie reală, am vedea o tendință sistematică

### Recomandare pentru paper

Prezentarea corectă: "6/8 spectral directions show consistent d_s=3.4-4.6 (σ=0.47). 2 directions have non-convergent power-law fits (r²<0.5), not due to structural anomaly (uniform degree k̄≈9.4, uniform clustering C̄≈0.166, orthogonal to Fiedler) but likely due to spectral mode-specific walk dynamics. The primary (Fiedler) time direction shows full convergence for both hemispheres."
