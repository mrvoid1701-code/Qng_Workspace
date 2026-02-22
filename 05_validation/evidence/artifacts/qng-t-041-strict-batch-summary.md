# QNG-T-041 C-086b v1 Strict Batch Summary

- Date: `2026-02-21`
- Mode: `amp-gate-mode=strict`
- Purpose: verify if preregistered `C-086b v1` amplitude band can pass under fixed, non-post-hoc trajectory subsets.

## Batch Design

- Full strict run: all non-control flyby science passes (`GALILEO_1`, `GALILEO_2`, `NEAR_1`, `ROSETTA_1`) + Pioneer anchor rows (`P10_EQ23`, `P11_EQ24`, `P10P11_FINAL`).
- Robustness strict runs: leave-one-flyby-out subsets, keeping the same Pioneer anchor rows.

## Result

- `5 / 5` strict runs -> `fail`.
- Common failure cause: `rule_pass_amp_band=False` (amplitude remains above preregistered band).
- Directional and cross-domain support remains present (`delta_chi2<0`, `directionality>=0.833`, Pioneer domain rules pass).

## Key Metrics Range (across strict batch)

- `delta_chi2`: `[-5970.164417, -4791.447388]`
- `directionality_score`: `[0.833333, 1.000000]`
- `sign_consistency`: `[0.800000, 1.000000]`
- `amp_median`: `[1.136333e-06, 3.669784e-06]` (all outside prereg band `1e-10..1e-8`)
- `tau_ratio_cross_domain`: `[11.104764, 19.002006]` (all pass cross-domain ratio gate)

## Machine-Readable Table

- `05_validation/evidence/artifacts/qng-t-041-strict-batch-summary.csv`
