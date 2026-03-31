# RESULT: QM Stage-1 G17b Failure Taxonomy v1

Date: 2026-03-04  
Language: EN

## Scope

Targeted diagnostic on `G17b` failures from frozen `qm-stage1-official-v5` summaries:

- primary: `DS-002/003/006`, seeds `3401..3600`
- attack: `DS-002/003/006`, seeds `3601..4100`
- holdout: `DS-004/008`, seeds `3401..3600`

No threshold changes. No formula changes.

## Headline

- total profiles: `2500`
- `G17b` fail profiles: `115`
- `G17b` fail rate: `4.60%`

## Dataset sensitivity

- `DS-006`: `115/700` fail (`16.43%`)
- `DS-002`: `0/700` fail
- `DS-003`: `0/700` fail
- `DS-004`: `0/200` fail
- `DS-008`: `0/200` fail

## Dominant fail classes

- `isolated_near_threshold`: `107`
- `coupled_g18_multipeak`: `5`
- `coupled_g19`: `2`
- `isolated_moderate_margin`: `1`

Interpretation: current `G17b` fragility is mostly isolated and near-threshold in `DS-006`, not broad lane collapse.

## Metric signals

Top correlation with `G17b` fail label:

- `g17b_propagator_slope`: `r = 0.356442`

Mean slope:

- fail cases: `-0.009502`
- pass cases: `-0.015177`

This is consistent with threshold-boundary concentration around the fixed `G17b` slope rule.

## Artifacts

- `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/g17b_fail_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/g17b_pass_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/qm-stage1-g17b-failure-taxonomy-v1/report.md`

## Next step (anti post-hoc)

Candidate-only `G17b` estimator hardening lane:

1. pre-register `G17b-v4` rule (no threshold edits),
2. run primary + attack + holdout,
3. require `degraded=0` and net uplift before any governance switch.
