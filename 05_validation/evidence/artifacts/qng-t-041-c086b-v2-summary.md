# QNG-T-041 C-086b2 Calibration Evaluation Summary

- Date: `2026-02-21`
- Prereg file: `05_validation/pre-registrations/qng-c-086b-amplitude-band-v2.md`
- Strict gate: `amp_band_min=1e-6`, `amp_band_max=6e-6` (locked before runs)

## Locked Evaluation Runs

- `E1`: flyby all-4 + pioneer (`P10_EQ23,P11_EQ24`)
- `E2`: flyby all-4 + pioneer (`P10_EQ23,P10P11_FINAL`)
- `E3`: flyby all-4 + pioneer (`P11_EQ24,P10P11_FINAL`)

## Outcome

- Strict amp gate result: `3/3 pass`.
- Directional/cross-domain support: `3/3 pass`.
- Day-equivalent support band (`1e-8..6e-8`): `0/3 pass` (reported note, not strict gate).
- Interpretation: calibration-lock consistency only; out-of-sample decision is tracked separately in `qng-t-041-c086b2-holdout-summary.md`.

## Key Numbers

- `amp_median` (all runs): `4.805263e-06` (inside v2 strict band).
- `amp_median_day_equiv` (all runs): `3.310185e-08` (outside v2 day-support band).
- `delta_chi2` range: `[-7700.199058, -4539.644615]`.

## Machine-Readable Table

- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-summary.csv`
