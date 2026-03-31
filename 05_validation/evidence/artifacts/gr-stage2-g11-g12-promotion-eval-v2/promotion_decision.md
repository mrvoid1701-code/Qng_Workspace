# GR Stage-2 G11/G12 Candidate Promotion Decision (v2)

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
- primary: PASS (improved `6`, degraded `0`)
- attack A: PASS (improved `25`, degraded `0`)
- attack B: PASS (improved `4`, degraded `0`)

2. `G12-v2 candidate`
- primary: PASS (`15/15` fail-cases recovered, degraded `0`)
- attack A: PASS (`103/108` fail-cases recovered, degraded `0`)
- attack B: PASS (`12/12` fail-cases recovered, degraded `0`)

3. `STAGE2 composite (with G11-v2 + G12-v2)`
- primary: PASS (improved `17`, degraded `0`)
- attack A: PASS (improved `101`, degraded `0`)
- attack B: PASS (improved `14`, degraded `0`)

## Decision

1. `G11a-v2` and `G12d-v2` satisfy prereg promotion criteria across primary + attacks.
2. Combined Stage-2 candidate package is promotion-ready.
3. Official Stage-2 switch remains an explicit governance step (separate commit/tag decision).
