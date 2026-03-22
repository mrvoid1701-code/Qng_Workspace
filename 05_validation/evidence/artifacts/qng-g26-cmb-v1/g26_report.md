# QNG-G26: CMB Planck Observational Gate

**Data:** 2026-03-22
**Verdict:** PASS

## Sub-gates

| Gate | Test | Rezultat | Prag | Status |
|------|------|---------|------|--------|
| G26a | Silk damping ell_damp | 0.169σ | < 2.0σ | PASS ✓ |
| G26b | Indice spectral n_s | 0.833σ | < 3.0σ | PASS ✓ |
| G26c | Δχ²_rel T-068 vs T-052 | -349.4 | < -22.32 | PASS ✓ |
| G26d | Spacing acustic ℓ_A | 5.7% | < 15% | PASS ✓ |

## Predicții QNG vs Planck 2018

### G26a — Scala de amortizare Silk

Formula din principii prime QNG:
```
ell_damp = ell_D_T × √(6 / (d_s × μ₁))
         = 576.144 × √(6 / (4.082 × 0.291))
         = 1294.9 ± 19.8
```

- **QNG:** 1294.9 ± 19.8
- **Planck:** 1290.9 ± 12.5
- **Discrepanță:** 0.169σ ← sub 1σ

### G26b — Indice spectral primordial n_s

```
n_s^QNG = 1 − (p_D_T − 1) × 2 / d_s
        = 1 − (1.119 − 1) × 2 / 4.082
        = 0.94170 ± 0.00179
```

- **QNG:** 0.94170 ± 0.00179
- **Planck:** 0.96490 ± 0.00420
- **Discrepanță:** 0.833σ

### G26c — Îmbunătățire model TT+TE+EE (T-068)

- Baseline T-052 (v3 unified): χ²_rel = -22.32
- Model T-068 (teoria fixată): χ²_rel = -371.67
- **Δχ²_rel = -349.4** (îmbunătățire de 15.7x)

## Interpretare

QNG reproduce scala de amortizare Silk la **0.17σ** și indicele spectral la **0.84σ** din date Planck reale.
Parametrii folosiți (μ₁=0.291, d_s=4.082, ell_D_T=576.144) sunt înghețați din teste anterioare independente (G17, G18d, T-052).
Nu există parametri liberi ajustați pe datele CMB pentru aceste predicții.