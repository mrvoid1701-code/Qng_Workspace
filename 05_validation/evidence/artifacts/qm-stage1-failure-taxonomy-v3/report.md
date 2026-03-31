# QM Stage-1 Failure Taxonomy (v1)

- generated_utc: `2026-03-04T09:47:33.575324Z`
- profiles_total: `2500`
- profiles_fail: `283`
- profiles_pass: `2217`
- fail_rate: `0.113200`

## Dominant Failing Gates

- `g18_status`: `160` fail occurrences across fail-cases
- `g17_status`: `120` fail occurrences across fail-cases
- `g19_status`: `11` fail occurrences across fail-cases

## Dominant Failing Subgates

- `g17b_status`: `115` fail occurrences across fail-cases
- `g17a_status_v2`: `5` fail occurrences across fail-cases

## Dataset Sensitivity

- `DS-006`: `139/700` fail (`0.198571`)
- `DS-003`: `69/700` fail (`0.098571`)
- `DS-004`: `14/200` fail (`0.070000`)
- `DS-008`: `14/200` fail (`0.070000`)
- `DS-002`: `47/700` fail (`0.067143`)

## Top 3 Hypothesized Mechanisms (No Changes Applied)

- Gate-dominant mechanism: `g18_status` is the dominant failing gate, suggesting lane failures are currently driven by that diagnostic family rather than a balanced multi-gate collapse.
- Feature-linked mechanism: `g18d_ds_local_agg` shows the strongest fail-correlation (`r=-0.784839`), suggesting residual Stage-1 failures cluster around specific geometric/spectral regimes.
- Coupling stability mechanism: `G20` remains stable (no G20 fails in lane-fail profiles), so post-switch failures are concentrated upstream (mostly G17/G18/G19 diagnostics) instead of semiclassical closure.

## Inputs

- official summaries:
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/summary.csv`
- promotion reports:
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## Promotion Eval Snapshots

- `qm-g18-primary-v3`: decision=`PASS` datasets=`DS-002,DS-003,DS-006`
- `qm-g18-attack-seed500-v3`: decision=`PASS` datasets=`DS-002,DS-003,DS-006`
- `qm-g18-attack-holdout-v3`: decision=`PASS` datasets=`DS-004,DS-008`

## Output Files

- `qm_fail_cases.csv`
- `qm_pass_cases.csv`
- `pattern_summary.csv`
- `feature_correlations.csv`
