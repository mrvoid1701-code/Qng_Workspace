# QNG-T-041 C-086b2 Holdout Summary

- Date: `2026-02-21`
- Prereg: `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`
- Strict gate: `amp_band_min=1e-6`, `amp_band_max=6e-6`

## Outcome

- Strict holdout result: `0/3 pass`.
- Shared fail pattern: `rule_pass_amp_band=False`, `rule_pass_pioneer_domain=False`, shuffle gates fail under low science-flyby count (`n_science_flyby=1`).
- Directionality/sign metrics remain positive (`1.0`) but are not sufficient to satisfy full strict release gate.

## Runs

| Run | Flyby IDs | Pioneer IDs | n_points | delta_chi2 | amp_median | amp_band | pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `H1` | `CASSINI_1,MESSENGER_1,EPOXI_1` | `P10_EQ23,P11_EQ24` | `3` | `-4408.640312` | `8.550000e-10` | `1.000000e-06..6.000000e-06` | `fail` |
| `H2` | `CASSINI_1,MESSENGER_1,EPOXI_2` | `P10_EQ23,P10P11_FINAL` | `3` | `-2432.777809` | `7.840000e-10` | `1.000000e-06..6.000000e-06` | `fail` |
| `H3` | `CASSINI_1,MESSENGER_1,EPOXI_5` | `P11_EQ24,P10P11_FINAL` | `3` | `-3268.859687` | `8.550000e-10` | `1.000000e-06..6.000000e-06` | `fail` |

## Machine-Readable Table

- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-summary.csv`
