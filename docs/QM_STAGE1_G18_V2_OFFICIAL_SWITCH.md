# QM Stage-1 Official Switch (G18d-v2 policy)

Date: 2026-03-03  
Effective tag: `qm-stage1-g18-v2-official`

## Why This Switch Exists

G18d-v2 candidate closed prereg promotion checks with:

1. primary uplift and zero degradation,
2. attack uplift and zero degradation,
3. holdout non-degradation and uplift.

Decision evidence:

- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.md`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.md`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.md`

## Frozen Official Policy (v3)

Official QM Stage-1 mapping is now:

1. `G17` official remains inherited from prior `v2` governance outputs.
2. `G18` official uses `G18-v2` candidate decision status (`G18d-v2`).
3. `G17-v1` and `G18-v1` remain legacy diagnostic-only.
4. `G19/G20` statuses remain inherited from frozen source runs.

No gate formulas or thresholds were changed.

## Candidate Evidence Snapshot

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `G18`: `551/600 -> 564/600`
- `QM lane`: `513/600 -> 526/600`
- `degraded_vs_v1 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `G18`: `1339/1500 -> 1395/1500`
- `QM lane`: `1255/1500 -> 1311/1500`
- `degraded_vs_v1 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `G18`: `360/400 -> 372/400`
- `QM lane`: `360/400 -> 372/400`
- `degraded_vs_v1 = 0`

## Governance Application Results (Official-v3 Apply)

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `G18`: `551/600 -> 564/600`
- `QM lane`: `513/600 -> 526/600`
- `degraded_vs_v1 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `G18`: `1339/1500 -> 1395/1500`
- `QM lane`: `1255/1500 -> 1311/1500`
- `degraded_vs_v1 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `G18`: `360/400 -> 372/400`
- `QM lane`: `360/400 -> 372/400`
- `degraded_vs_v1 = 0`

Regression guard (`primary + attack + holdout`):

- decision: `PASS`
- profile drift: `none`
- official pass-rate degradation: `none`

## Implementation

Official policy application runner:

- `scripts/tools/run_qm_stage1_official_v3.py`

Expected output package roots:

- `05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600/`
