# GR Stage-2 G11/G12 Candidate Promotion Decision (v1)

Date: 2026-03-02

## Inputs

Primary evaluation:

- `primary_ds002_003_006_s3401_3600/report.json`

Attack A (new seed block):

- `attack_seed500_ds002_003_006_s3601_4100/report.json`

Attack B (holdout datasets):

- `attack_holdout_ds004_008_s3401_3600/report.json`

## Frozen Criteria

- zero degraded vs v1
- net uplift on v1 fail-cases
- per-dataset non-degradation

## Observed Outcomes

1. `G11-v2 candidate`
- primary: FAIL (improved `0`, degraded `0`, no fail-case uplift)
- attack A: FAIL (improved `0`, degraded `0`, no fail-case uplift)
- attack B: FAIL (improved `0`, degraded `0`, no fail-case uplift)

2. `G12-v2 candidate`
- primary: PASS (`15/15` fail-cases recovered, degraded `0`)
- attack A: PASS (`103/108` fail-cases recovered, degraded `0`)
- attack B: PASS (`12/12` fail-cases recovered, degraded `0`)

3. `STAGE2 composite (with G11-v2 + G12-v2)`
- improved in all runs
- degraded `0` in all runs
- overall promotion package remains FAIL because `G11-v2` does not satisfy uplift criterion

## Decision

1. `G12d-v2`: promotion-ready candidate (passes primary + attacks under frozen criteria).
2. `G11a-v2`: NOT promotion-ready (no uplift over v1 fail-cases).
3. Stage-2 official switch for combined `G11+G12` package: **deferred** until a new `G11` candidate shows uplift under prereg.
