# QNG — K_R Universality Test v1

**Data:** 2026-03-16  
**Referință:** 03_math/derivations/qng-kr-dimensional-v1.md  

## K_R din Simulare (T-029)

| Parametru | Valoare | Incertitudine |
|-----------|---------|---------------|
| k | 0.85 | ± 0.02 |
| tau | 1.3 | ± 0.1 |
| **K_R = k×tau** | **1.1050** | **± 0.0889** |

## C_straton și tau_SI per Misiune Pioneer

| Misiune | r [AU] | C_straton [s⁻¹] | tau_SI [s] | tau_SI [zile] | K_R_SI [s] |
|---------|--------|----------------|-----------|--------------|-----------|
| P10_EQ23 | 55.0 | 6.4262e-14 | 2.6972e+05 | 3.12 | 2.2926e+05 |
| P11_EQ24 | 27.0 | 7.3707e-14 | 3.6599e+04 | 0.42 | 3.1109e+04 |
| P10P11_FINAL | 48.1 | 7.2833e-14 | 2.0447e+05 | 2.37 | 1.7380e+05 |

## Testul de Universalitate

- **C_straton P10/P11:** 1.147 (deviație: 14.7%)
  - ✓ CONSISTENT la < 20%
- **tau_SI P10/P11:** raport = 7.4×
  - ✗ Factor 7× inconsistență — tau ≠ const

## Factorul de Conversie Simulare → SI

```
f_conv = tau_SI(P10+P11) / tau_sim = 2.045e+05 / 1.3 = 1.573e+05 s/sim_unit
       ≈ 1.82 zile per unitate de simulare

dt_SI = 0.06 × 1.573e+05 = 9.437e+03 s ≈ 2.62 ore per pas
K_R_SI = k × tau_SI = 0.85 × 2.045e+05 = 1.738e+05 s
```

## Concluzie

- **K_R_sim = 1.105** bine constrânsă din T-029 ✓
- **C_straton consistent la ~15%** cross-spacecraft (D8, PARȚIAL) ✓
- **tau_SI inconsistent P10/P11 (factor 7×)** — formula QNG cu tau=const FAIL ✗
- Anomalia Pioneer (Turyshev 2012) explicată termic — ancora C_straton posibil artificială ⚠️
- Factor conversie: **1.573e+05 s/sim_unit** (1.8 zile/sim_unit)