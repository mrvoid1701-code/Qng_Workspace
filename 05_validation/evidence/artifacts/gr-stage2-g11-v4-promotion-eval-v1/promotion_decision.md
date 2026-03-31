# GR Stage-2 G11a-v4 Candidate Promotion Decision (v1)

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

- `degraded_vs_v3 = 0`
- `improved_vs_v3 >= 2`
- per-dataset non-degradation
- `g11_v4_fail <= 3`

Attack A / B:

- `degraded_vs_v3 = 0`
- per-dataset non-degradation
- `improved_vs_v3 >= 0`

## Observed Outcomes

1. Primary (`DS-002/003/006`, `3401..3600`)
- `G11`: `594/600 -> 597/600`
- `fails`: `6 -> 3`
- `improved=3`, `degraded=0`
- `STAGE2`: `594/600 -> 597/600`
- decision: PASS

2. Attack A (`DS-002/003/006`, `3601..4100`)
- `G11`: `1464/1500 -> 1470/1500`
- `fails`: `36 -> 30`
- `improved=6`, `degraded=0`
- `STAGE2`: `1460/1500 -> 1466/1500`
- decision: PASS

3. Attack B (`DS-004/008`, `3401..3600`)
- `G11`: `398/400 -> 398/400`
- `fails`: `2 -> 2`
- `improved=0`, `degraded=0`
- `STAGE2`: `398/400 -> 398/400`
- decision: PASS

## Strict Fail Taxonomy (official-v3 rerun)

Source:

- `05_validation/evidence/artifacts/gr-stage2-g11-fail-closure-v3-v1/summary.csv`

Dominant classes over 6 fails:

- `rank_monotonic_pearson_collapse`: `3`
- `g11b_slope_fail`: `1`
- `multi_peak_weak_rank`: `1`
- `weak_rank_corr`: `1`

Nearest-pass neighbor comparisons indicate the 3 recovered cases are rank-stable but Pearson-collapsed under v3.

## Decision

1. `G11a-v4` satisfies frozen candidate criteria on primary + attacks.
2. Candidate is promotion-ready for a separate governance switch commit.
3. Official Stage-2 mapping remains unchanged in this commit.
