# Pre-Registration: QNG-C-086b2 Holdout v1

- Claim fragment: `C-086b2` (numeric amplitude scaling, out-of-sample gate)
- Parent claim: `QNG-C-086`
- Created: `2026-02-21`
- Status: executed, fail (`0/3` strict holdout pass)
- Governance note: `C-086b v1` is permanent fail history; `C-086b2` is calibration-derived and must prove out-of-sample.
- Registry: `05_validation/pre-registrations/holdout-registry.csv` (append-only)

## Locked Inputs

- Runner: `scripts/run_qng_t_028_trajectory_real.py`
- Dataset: `DS-005` flyby + Pioneer anchor
- Amp gate: `strict`
- Band lock: `amp_band_min=1.0e-06`, `amp_band_max=6.0e-06`
- Non-gating diagnostic band: `1.0e-08 <= amp_median_day_equiv <= 6.0e-08`
- Same gates as prior trajectory runs; no gate edits allowed.

## Locked Holdout Sets (Not Used In b2 Calibration Lock)

- `H1`: flyby=`CASSINI_1,MESSENGER_1,EPOXI_1`; pioneer=`P10_EQ23,P11_EQ24`
- `H2`: flyby=`CASSINI_1,MESSENGER_1,EPOXI_2`; pioneer=`P10_EQ23,P10P11_FINAL`
- `H3`: flyby=`CASSINI_1,MESSENGER_1,EPOXI_5`; pioneer=`P11_EQ24,P10P11_FINAL`

## Promotion Rule

- Promote `C-086b2` to real prediction only if all holdout runs pass strict gating without any threshold/model edits.
- Any holdout fail keeps `C-086b2` in pending/fail state.

## Post-Lock Execution

- Execution date: `2026-02-21`
- Result: `0/3` strict holdout pass.
- Artifact index:
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h2/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-h3/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-t-041-c086b2-holdout-summary.md`

## Known Scope Limit

- DS-005 currently has only one non-control flyby pass outside the calibration flyby set (`CASSINI_1`).
- Holdout evidence is valid under current data inventory but remains bandwidth-limited until additional non-control real flyby missions are ingested.
