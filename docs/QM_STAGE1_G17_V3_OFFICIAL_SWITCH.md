# QM Stage-1 Official Switch (G17-v3 policy)

Date: 2026-03-04  
Effective tag: `qm-stage1-g17-v3-official`

## Why This Switch Exists

G17-v3 candidate passed prereg promotion checks on primary, attack, and holdout with zero degradation.

Decision evidence:

- `05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g17-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## Frozen Official Policy (v4)

Official QM Stage-1 mapping is now:

1. `G17` official uses `G17-v3` decision status.
2. `G18` official remains inherited from official-v3 (`G18-v2` policy).
3. `G19/G20` remain inherited unchanged.
4. `G17-v1` and `G18-v1` remain legacy diagnostics.

No gate formulas or thresholds were changed.

## Governance Application Results

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `G17`: `439/600 -> 564/600`
- `QM lane`: `411/600 -> 513/600`
- `degraded_vs_v2 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `G17`: `1092/1500 -> 1416/1500`
- `QM lane`: `1017/1500 -> 1255/1500`
- `degraded_vs_v2 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `G17`: `356/400 -> 400/400`
- `QM lane`: `322/400 -> 360/400`
- `degraded_vs_v2 = 0`

Official governance packages:

- `05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/`

## Baseline + Guard (v2)

Baseline and guard were rebuilt over official-v4 outputs:

- baseline root: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/`
- latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v2/latest_check/regression_report.json`
- decision: `PASS`

## Post-switch Taxonomy (v2)

- package: `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/`
- total profiles: `2500`
- fail profiles: `372` (`14.88%`)
- dominant failing gate remains `G18` (`250` fail occurrences)

## Implementation

Official policy applier:

- `scripts/tools/run_qm_stage1_official_v4.py`

Candidate evaluator:

- `scripts/tools/run_qm_g17_candidate_eval_v3.py`
