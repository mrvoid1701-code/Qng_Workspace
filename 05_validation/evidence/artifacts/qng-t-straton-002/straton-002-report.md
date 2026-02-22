# QNG-T-STRATON-002 Report
Authored by: Claude Sonnet 4.6

- Dataset: DS-005 classic subset — n=13 rows, 6 missions
- Excluded: JUNO_1, BEPICOLOMBO_1, SOLAR_ORBITER_1 (placeholder residuals)

## BIC Decomposition

| Model | k | n | LL | BIC | chi2 | param |
| --- | --- | --- | --- | --- | --- | --- |
| A (null)    | 1 | 13 | -2309.9758 | 4622.5165 | 5028.5981 | tau_const=-1.0255e-03 |
| B (straton) | 1 | 13 | -5075.5719 | 10153.7087 | 10559.7903 | alpha=-3.7101e-07 |
| delta (B-A) | - | - | -2765.5961 | 5531.1922 | 5531.1922 | - |

## Sigma Summary

| min | median | max |
| --- | --- | --- |
| 5.0772e-10 | 7.8954e-08 | 1.2596e-06 |

## Gates

| Gate | Threshold | Value | Status |
| --- | --- | --- | --- |
| G1 delta_bic | <= -10 | 5531.1922 | FAIL |
| G2 alpha CV | < 0.30 | 1.607 | FAIL |
| G3 shuffle median | > -2.0 | 1442.303 | PASS |
| G4 LOO fraction | >= 0.90 | 0.077 (1/13) | FAIL |

**Decision: FAIL**

## Residuals Diagnostic (D4)

| pass_id | mass_kg | sigma | std_resid_A | std_resid_B | leverage |
| --- | --- | --- | --- | --- | --- |
| GALILEO_1 | 2223 | 7.4885e-08 | 67.145 | 63.593 | YES |
| GALILEO_2 | 2223 | 1.0534e-06 | -1.508 | -2.113 | YES |
| NEAR_1 | 805 | 1.1983e-07 | 21.181 | 79.554 | YES |
| CASSINI_1 | 5600 | 1.2596e-06 | -1.691 | -1.375 | no |
| ROSETTA_1 | 3000 | 1.8932e-08 | -7.657 | -13.430 | YES |
| MESSENGER_1 | 1107 | 5.9500e-09 | -2.724 | 0.108 | no |
| ROSETTA_2 | 3000 | 5.3867e-07 | -0.193 | -0.209 | no |
| EPOXI_1 | 650 | 1.5998e-07 | -0.059 | -0.014 | no |
| EPOXI_2 | 650 | 5.3999e-08 | -0.138 | -0.032 | no |
| ROSETTA_3 | 3000 | 7.5342e-07 | -0.392 | -0.425 | no |
| EPOXI_3 | 650 | 6.3109e-10 | -0.000 | -0.000 | no |
| EPOXI_4 | 650 | 5.0772e-10 | 0.000 | 0.000 | no |
| EPOXI_5 | 650 | 7.8954e-08 | 0.276 | 0.065 | no |

## LOO Row Influence (D1)

| pass_id | mission | mass_kg | delta_alpha_rel_pct | delta_bic_loo | gate |
| --- | --- | --- | --- | --- | --- |
| GALILEO_1 | Galileo | 2223 | -15.5% | 5981.85 | LEVERAGE |
| GALILEO_2 | Galileo | 2223 | 0.1% | 5529.00 | LEVERAGE |
| NEAR_1 | NEAR | 805 | 34.0% | -381.21 | OK |
| CASSINI_1 | Cassini | 5600 | 0.0% | 5532.16 | LEVERAGE |
| ROSETTA_1 | Rosetta | 3000 | -123.5% | 4229.26 | LEVERAGE |
| MESSENGER_1 | Messenger | 1107 | 0.0% | 5538.62 | LEVERAGE |
| ROSETTA_2 | Rosetta | 3000 | -0.0% | 5531.19 | LEVERAGE |
| EPOXI_1 | EPOXI | 650 | -0.0% | 5531.20 | LEVERAGE |
| EPOXI_2 | EPOXI | 650 | -0.0% | 5531.21 | LEVERAGE |
| ROSETTA_3 | Rosetta | 3000 | -0.0% | 5531.16 | LEVERAGE |
| EPOXI_3 | EPOXI | 650 | -0.0% | 5531.19 | LEVERAGE |
| EPOXI_4 | EPOXI | 650 | -0.0% | 5531.19 | LEVERAGE |
| EPOXI_5 | EPOXI | 650 | -0.0% | 5531.26 | LEVERAGE |

## LOO Mission Influence (D2)

| mission_id | n_rows | delta_alpha_rel_pct | delta_bic_loo | gate |
| --- | --- | --- | --- | --- |
| Cassini | 1 | 0.0% | 5532.16 | LEVERAGE |
| EPOXI | 5 | -0.0% | 5531.29 | LEVERAGE |
| Galileo | 2 | -15.5% | 5980.25 | LEVERAGE |
| Messenger | 1 | 0.0% | 5538.62 | LEVERAGE |
| NEAR | 1 | 34.0% | -381.21 | OK |
| Rosetta | 3 | -123.5% | 4228.35 | LEVERAGE |

## Model C: Power Law (diagnostic only)

BIC penalty for k=2 vs k=1: ln(13) = 2.5649

| | Grid (locked) | Continuous (cross-check) |
| --- | --- | --- |
| best beta | 0.1 | 0.1000 |
| best alpha_c | -4.8627e-04 | -4.8627e-04 |
| LL | -2523.8174 | -2523.8185 |
| BIC (k=2) | 5052.7648 | 5052.7669 |
| grid vs continuous diff | 0.0000 | - |

- delta_bic(C-A): 430.2483
- delta_bic(C-B): -5100.9440  (C preferred over B)
- delta_ll(C-B): 2551.7545
- beta 95% CI (bootstrap n=500): [0.10, 2.95]