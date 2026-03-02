# GR Stage-2 G11a-v3 Candidate Promotion Decision (v1)

Date: 2026-03-02

## Inputs

Primary:

- `primary_ds002_003_006_s3401_3600/report.json`

Attack A:

- `attack_seed500_ds002_003_006_s3601_4100/report.json`

Attack B (holdout):

- `attack_holdout_ds004_008_s3401_3600/report.json`

## Frozen Criteria

Primary:

- `degraded_vs_v2 = 0`
- `improved_vs_v2 >= 5`
- per-dataset non-degradation
- `weak_corr_drop >= 2`

Attack A / B:

- `degraded_vs_v2 = 0`
- `improved_vs_v2 >= 1`
- weak-corr drop non-negative (A uses `>=1`, B uses `>=0` in this run config)

## Observed Outcomes

1. Primary (`DS-002/003/006`, `3401..3600`)
- `G11`: `587/600 -> 594/600`
- `improved=7`, `degraded=0`
- `weak_corr_fail_count: 12 -> 5` (`drop=7`)
- decision: PASS

2. Attack A (`DS-002/003/006`, `3601..4100`)
- `G11`: `1451/1500 -> 1464/1500`
- `improved=13`, `degraded=0`
- `weak_corr_fail_count: 47 -> 35` (`drop=12`)
- decision: PASS

3. Attack B (`DS-004/008`, `3401..3600`)
- `G11`: `394/400 -> 398/400`
- `improved=4`, `degraded=0`
- `weak_corr_fail_count: 5 -> 1` (`drop=4`)
- decision: PASS

## Decision

1. `G11a-v3` satisfies prereg candidate criteria on primary + attacks.
2. Candidate is promotion-ready for a dedicated governance switch commit.
3. Official Stage-2 policy remains unchanged in this commit (candidate-only closure).
