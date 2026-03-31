# QNG — K_R Universality Test: N-body ↔ Galactic Scale

**Data:** 2026-03-16  
**Dataset:** SPARC DS-006 — 175 galaxii, 3391 puncte  

## Rezultat Principal

| Context | Scara | k | Sursa |
|---------|-------|---|-------|
| T-029 N-body | ~pc (abstract) | 0.8500 ± 0.0200 | chi2, 12 seeds |
| SPARC M8c | ~kpc (galactic) | 0.8402 | 175 galaxii |
| Teorie cubică | — | 0.8367 | (2-√2)^(1/3) |
| **Δk N-body↔gal** | | **1.15%** | **✓ UNIVERSAL** |

## g† — Parametru Derivat (nu liber)

- g†_teorie = (2-√2) × a₀ = 7.0294e-11 m/s²
- g†_fit    = 7.1797e-11 m/s²
- Deviație  = 2.14%  ⚠

## Performanța M8c vs MOND

| Model | Param | χ²/N | ΔAIC vs MOND |
|-------|-------|------|-------------|
| Null | 0 | 302.46 | +705423 |
| MOND | 1 | 94.43 | 0 (ref) |
| M8c | 2 | 80.27 | -48024 ✓ |

## Distribuția k per Galaxie

- k_mean = 0.8251
- k_std  = 0.8979
- CV(k)  = 1.0882  (⚠ variabil)
- Range: [0.010, 10.000]

## Ierarhia K_R

```
K_R = k × tau
k    = 0.850  ← UNIVERSAL (N-body ≈ galactic la 1.15%)
tau  = scala-specifica (T-029: 1.3, Pioneer: ~2×10⁵ s, gal: TBD)
```

## Predicție Falsificabilă

Orice set de date nou trebuie să producă k ∈ [0.790, 0.910] (3σ).
g† nu este parametru liber — valoarea sa este (2-√2)×a₀.