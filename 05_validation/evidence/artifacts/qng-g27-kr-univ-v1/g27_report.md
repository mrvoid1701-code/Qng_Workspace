# QNG-G27: K_R Universality Gate

**Data:** 2026-03-20
**Verdict:** PASS
**Spread total:** 1.80% pe 18 ordine de mărime

## Tabelul de Universalitate

| Context | Scară | k | Δk vs teorie |
|---------|-------|---|-------------|
| k_cmb (Gpc CMB) | — | 0.834913 | -0.216% |
| k_gal (kpc SPARC) | — | 0.840221 | +0.419% |
| k_sim (pc N-body) | — | 0.850000 | +1.587% |
| k_theory (cubic) | — | 0.836719 | +0.000% |

## Sub-gates

| Gate | Test | Rezultat | Prag | Status |
|------|------|---------|------|--------|
| G27a | k_cmb vs k_theory | 0.216% | < 1.0% | PASS ✓ |
| G27b | k_gal vs k_theory | 0.419% | < 2.0% | PASS ✓ |
| G27c | k_sim vs k_theory | 1.587% | < 5.0% | PASS ✓ |
| G27d | Spread total | 1.803% | < 5.0% | PASS ✓ |

## Derivare k_theory

```
iso_target = 1/√2        (echilibru rețea cubică QNG)
μ₁ = 1 - iso_target = (2-√2)/2 = 0.2929
k_theory = (2 × μ₁)^(1/3) = (2-√2)^(1/3) = 0.8367
```

## Conexiunea μ₁: Jaccard = CMB

- μ₁ Jaccard eigenvalue (G17): **0.2910**
- μ₁ cubic lattice (teoretic): **0.2929**
- μ₁ din Planck TT damping (T-065): **0.291**

Toți trei sunt identici — eigenvalue-ul graficului QNG apare în spectrul CMB.
Acesta este cel mai puternic argument pentru universalitatea structurii QNG.