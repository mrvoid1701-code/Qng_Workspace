# GR Stage-3 Official Switch (G11/G12 v5 policy)

Date: 2026-03-04  
Effective tag: `gr-stage3-g11-v5-official`

## Why This Switch Exists

G11 candidate-v5 closed the remaining Stage-3 primary fail set with zero degradation.

Decision evidence:

- `05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/gr-stage3-g11-promotion-eval-v5/attack_holdout_ds004_008_s3401_3600/report.json`

## Frozen Official Policy (v5)

Official Stage-3 mapping is now:

1. `G11` official uses candidate-v5 decision status.
2. `G12` official uses candidate-v5 decision status.
3. `G7/G8/G9` statuses remain inherited from frozen source runs.

No gate formulas or thresholds were changed.

## Governance Application Results

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `STAGE3`: `597/600 -> 600/600`
- `improved_vs_v3 = 3`
- `degraded_vs_v3 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `STAGE3`: `1433/1500 -> 1459/1500`
- `improved_vs_v3 = 26`
- `degraded_vs_v3 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `STAGE3`: `398/400 -> 400/400`
- `improved_vs_v3 = 2`
- `degraded_vs_v3 = 0`

Official governance packages:

- `05_validation/evidence/artifacts/gr-stage3-official-v5/`
- `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-seed500-v1/`
- `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-holdout-v1/`

## Baseline + Guard (v2)

Rebuilt Stage-3 baseline for official-v5 and executed guard:

- baseline: `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v2/gr_stage3_baseline_official.json`
- latest check: `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v2/latest_check/regression_report.json`
- decision: `PASS`

## Implementation

Official policy applier:

- `scripts/tools/run_gr_stage3_official_v3.py`

Candidate evaluator:

- `scripts/tools/run_gr_stage3_g11_candidate_eval_v5.py`
