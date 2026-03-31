# QM Stage-1 Failure Taxonomy (v1)

- generated_utc: `2026-03-04T09:30:12.659119Z`
- profiles_total: `2500`
- profiles_fail: `372`
- profiles_pass: `2128`
- fail_rate: `0.148800`

## Dominant Failing Gates

- `g18_status`: `250` fail occurrences across fail-cases
- `g17_status`: `120` fail occurrences across fail-cases
- `g19_status`: `11` fail occurrences across fail-cases

## Dominant Failing Subgates

- `g17b_status`: `115` fail occurrences across fail-cases
- `g17a_status_v2`: `5` fail occurrences across fail-cases

## Dataset Sensitivity

- `DS-006`: `158/700` fail (`0.225714`)
- `DS-003`: `107/700` fail (`0.152857`)
- `DS-004`: `20/200` fail (`0.100000`)
- `DS-008`: `20/200` fail (`0.100000`)
- `DS-002`: `67/700` fail (`0.095714`)

## Top 3 Hypothesized Mechanisms (No Changes Applied)

- Gate-dominant mechanism: `g18_status` is the dominant failing gate, suggesting lane failures are currently driven by that diagnostic family rather than a balanced multi-gate collapse.
- Feature-linked mechanism: `g17c_e0_per_mode` shows the strongest fail-correlation (`r=-0.223472`), suggesting residual Stage-1 failures cluster around specific geometric/spectral regimes.
- Coupling stability mechanism: `G20` remains stable (no G20 fails in lane-fail profiles), so post-switch failures are concentrated upstream (mostly G17/G18/G19 diagnostics) instead of semiclassical closure.

## Inputs

- official summaries:
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/summary.csv`
- promotion reports:
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
  - `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## Promotion Eval Snapshots

- `qm-g17-primary-v3`: decision=`PASS` datasets=`DS-002,DS-003,DS-006`
- `qm-g17-attack-seed500-v3`: decision=`PASS` datasets=`DS-002,DS-003,DS-006`
- `qm-g17-attack-holdout-v3`: decision=`PASS` datasets=`DS-004,DS-008`

## Output Files

- `qm_fail_cases.csv`
- `qm_pass_cases.csv`
- `pattern_summary.csv`
- `feature_correlations.csv`
