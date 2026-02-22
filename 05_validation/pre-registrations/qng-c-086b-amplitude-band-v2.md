# Pre-Registration: QNG-C-086b2 Calibration Band v2

- Claim fragment: `C-086b2` (calibration branch for numeric amplitude scaling)
- Parent claim: `QNG-C-086`
- Created: `2026-02-21`
- Status: calibration-locked (not a confirmed prediction)
- Relation to v1: `C-086b v1` remains falsified and archived.

## Purpose

- This file defines a locked calibration band after `C-086b v1` falsification.
- Passing this file alone does not validate prediction power.
- Prediction status is decided only by a separate out-of-sample holdout prereg.

## Locked Policies

- Same sample policy: baseline vs memory uses identical rows.
- Same sigma policy: published uncertainties are unchanged.
- Same likelihood policy: weighted chi-square on identical rows.
- No post-hoc band edits after this file timestamp.

## Calibration Window (Used To Define b2 Band)

- Source artifacts:
- `05_validation/evidence/artifacts/qng-t-041-strict-full/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-g1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-g2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-near/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-strict-loo-rosetta/fit-summary.csv`

## Locked b2 Band

- Perigee-window strict gate (runner gate):
- `1.0e-06 <= amp_median <= 6.0e-06` m/s^2
- Day-equivalent support band (diagnostic, non-gating):
- `1.0e-08 <= amp_median_day_equiv <= 6.0e-08` m/s^2

## In-Sample Locked Check

- `E1`: flyby=`GALILEO_1,GALILEO_2,NEAR_1,ROSETTA_1`; pioneer=`P10_EQ23,P11_EQ24`
- `E2`: flyby=`GALILEO_1,GALILEO_2,NEAR_1,ROSETTA_1`; pioneer=`P10_EQ23,P10P11_FINAL`
- `E3`: flyby=`GALILEO_1,GALILEO_2,NEAR_1,ROSETTA_1`; pioneer=`P11_EQ24,P10P11_FINAL`

## Recorded Outcome

- Execution date: `2026-02-21`
- Result: `3/3` strict pass on calibration-locked checks.
- Interpretation: calibration consistency only; not out-of-sample confirmation.
- Artifact index:
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-e3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b-v2-summary.md`

## Next Required Gate

- Out-of-sample validation is locked in:
- `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`
- Current holdout state (`2026-02-21`): `0/3` strict holdout pass (`C-086b2` remains pending/fail).
