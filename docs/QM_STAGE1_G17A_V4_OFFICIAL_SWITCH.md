# QM Stage-1 G17a-v4 Official Switch

Date: 2026-03-05  
Effective tag: `qm-stage1-g17a-v4-official`

## Decision

QM Stage-1 official policy is switched from `official-v9` to `official-v10` using `G17a-v4` candidate outputs (governance layer only, no physics threshold/formula edits).

## Candidate Policy

- Candidate runner: `scripts/tools/run_qm_g17a_candidate_eval_v4.py`
- Scope:
  - preserves source official decisions by default
  - recovery only for `g17a-only` fail profiles (`g17b/c/d` pass, multi-peak flag true)
  - multi-window local-gap check across fixed basin quantiles
  - same `G17a` threshold parsed from metric checks (`>0.01`)

## Promotion Evidence (PASS)

- Primary (`DS-002/003/006`, seeds `3401..3600`):
  - `QM lane: 590/600 -> 591/600`, degraded=`0`
- Attack (`DS-002/003/006`, seeds `3601..4100`):
  - `QM lane: 1475/1500 -> 1479/1500`, degraded=`0`
- Holdout (`DS-004/008`, seeds `3401..3600`):
  - `QM lane: 400/400 -> 400/400`, degraded=`0`

Promotion packages:

- `05_validation/evidence/artifacts/qm-g17a-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g17a-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g17a-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## Official-v10 Outputs

- `05_validation/evidence/artifacts/qm-stage1-official-v10/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v10/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v10/attack_holdout_ds004_008_s3401_3600/`

Totals:

- `2470/2500` QM-lane pass (`98.8%`)

## Baseline/Guard Refresh

- baseline directory: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v8/`
- guard latest check: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v8/latest_check/`
- decision: `PASS`

## Stage-2 Projection Snapshot

Using Stage-2 raw summaries projected through `official-v10`:

- raw pass: `1750/2500`
- official pass: `2470/2500`
- improved (`fail->pass`): `720`
- degraded (`pass->fail`): `0`
