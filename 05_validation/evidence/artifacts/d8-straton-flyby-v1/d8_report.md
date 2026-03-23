# D8 — QNG Straton Flyby Test

**Data:** 2026-03-23  
**C_straton:** 6.992e-14 s⁻¹ (calibrat pe Pioneer P10+P11)  

## Model

```
a_lag = -C × v_r  (radial inward, din Scenario B + VPC)
C = a_P10P11 / v_r,Pioneer = 8.74×10⁻¹⁰ / 12500 = 6.99×10⁻¹⁴ s⁻¹
```

Pentru flyby terestru: `Δv∞ ≈ -(C/v∞) × ∫ v_r² dt`

## Pioneer (calibrare)

| Pass | v_r km/s | a_pred | a_obs | pull |
|------|---------|--------|-------|------|
| P10_EQ23 | 12.2 | 8.530e-10 | 7.840e-10 | -4.3σ |
| P11_EQ24 | 11.6 | 8.111e-10 | 8.550e-10 | +2.9σ |
| P10P11_FINAL | 12.0 | 8.390e-10 | 8.740e-10 | +0.3σ |

## Flyby Terestre

| Pass | Δv_strat mm/s | Δv_obs mm/s | σ | Categorie |
|------|-------------|-----------|---|-----------|
| GALILEO_1 | -0.0022 | +3.920 | 0.080 | Anderson2008 |
| GALILEO_2 | -0.0026 | -4.600 | 1.000 | control |
| NEAR_1 | -0.0044 | +13.460 | 0.130 | Anderson2008 |
| CASSINI_1 | -0.0004 | -2.000 | 1.000 | control |
| ROSETTA_1 | -0.0100 | +1.800 | 0.030 | Anderson2008 |
| MESSENGER_1 | -0.0090 | +0.020 | 0.010 | Anderson2008 |
| ROSETTA_2 | -0.0009 | +0.000 | 1.000 | control |
| EPOXI_1 | -0.0043 | +0.000 | 1.000 | control |
| EPOXI_2 | -0.0009 | +0.000 | 1.000 | control |
| ROSETTA_3 | -0.0015 | +0.000 | 1.000 | control |
| EPOXI_3 | -0.0000 | +0.000 | 1.000 | control |
| EPOXI_4 | -0.0000 | +0.000 | 1.000 | control |
| EPOXI_5 | -0.0019 | +0.000 | 1.000 | control |
| JUNO_1 | -0.0016 | +0.000 | 1.000 | null_modern |
| BEPICOLOMBO_1 | -0.0042 | +0.000 | 1.000 | null_modern |
| SOLAR_ORBITER_1 | -0.0016 | +0.000 | 1.000 | null_modern |

## Concluzie

- **Pioneer:** 2/3 în 3σ ✓
- **Anderson (2008):** Straton prezice Δv ~ -0.01 mm/s (negativ, factor 1000× sub observat). **Nu sunt explicate.**
  Fizica Anderson necesită un mecanism separat (posibil cuplaj cu rotația Pământului în QNG).
- **Nulluri moderne (Juno, BepiColombo, Solar Orbiter):** 3/3 consistente cu predicție straton. ✓

### De ce straton nu poate explica Anderson anomalii

VPC implică `a_lag ∝ v_r` (radial). Puterea instantanee `P = -C v_r² ≤ 0` mereu.
=> Energia scade => Δv∞ < 0 mereu.
Anderson anomalii sunt **pozitive** (+1.8 to +13.5 mm/s) → cer cuplaj cu alt câmp
(rotație, câmp magnetic, sau termen QNG non-VPC).

Aceasta este o predicție falsificabilă: dacă un mecanism QNG suplimentar
(**fără** VPC) produce Δv > 0 cu formula δv/v = 2ωR/c × (cosδ_in − cosδ_out),
atunci QNG unifică Pioneer + flyby. Altfel, flyby anomalii au altă origine.