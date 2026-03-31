# QM Stage-1 Official Switch (G18-v3 policy)

Date: 2026-03-04  
Effective tag: `qm-stage1-g18-v3-official`

## Why This Switch Exists

G18-v3 candidate passed prereg promotion checks on primary, attack, and holdout with zero degradation.

Decision evidence:

- `05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## Frozen Official Policy (v5)

Official QM Stage-1 mapping is now:

1. `G17` official remains inherited from official-v4 (`G17-v3` policy).
2. `G18` official uses `G18-v3` decision status.
3. `G19/G20` remain inherited unchanged.
4. `G17-v1` and `G18-v1` remain legacy diagnostics.

No gate formulas or thresholds were changed.

## Governance Application Results

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `G18`: `551/600 -> 568/600`
- `QM lane`: `513/600 -> 529/600`
- `degraded_vs_v4 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `G18`: `1339/1500 -> 1400/1500`
- `QM lane`: `1255/1500 -> 1316/1500`
- `degraded_vs_v4 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `G18`: `360/400 -> 372/400`
- `QM lane`: `360/400 -> 372/400`
- `degraded_vs_v4 = 0`

Official governance packages:

- `05_validation/evidence/artifacts/qm-stage1-official-v5/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v5/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v5/attack_holdout_ds004_008_s3401_3600/`

## Baseline + Guard (v3)

Baseline and guard were rebuilt over official-v5 outputs:

- baseline root: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/`
- latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v3/latest_check/regression_report.json`
- decision: `PASS`

## Post-switch Taxonomy (v3)

- package: `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v3/`
- total profiles: `2500`
- fail profiles: `283` (`11.32%`)
- dominant failing gate remains `G18`, but reduced from `250` to `160` fail occurrences

## Implementation

Official policy applier:

- `scripts/tools/run_qm_stage1_official_v3.py` (policy id `qm-stage1-official-v5`)

Candidate evaluator:

- `scripts/tools/run_qm_g18_candidate_eval_v3.py`
