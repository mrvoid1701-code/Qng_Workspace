# QM Stage-2 Failure Taxonomy (v1)

- generated_utc: `2026-03-04T08:44:22.134165+00:00`
- profiles_total: `2500`
- fail_profiles: `750`
- pass_profiles: `1750`
- fail_rate: `0.300000`
- dominant_failing_gate: `g17_status`

## Fail Rate by Block

- `attack_ds002_003_006_s3601_4100`: fail `483/1500`
- `holdout_ds004_008_s3401_3600`: fail `78/400`
- `primary_ds002_003_006_s3401_3600`: fail `189/600`

## Dataset Sensitivity

- `DS-002`: fail `196/700`
- `DS-003`: fail `250/700`
- `DS-004`: fail `39/200`
- `DS-006`: fail `226/700`
- `DS-008`: fail `39/200`

## Top Fail Signatures

- `g17_status`: `489`
- `g18_status`: `128`
- `g17_status+g18_status`: `122`

## Top 3 Hypothesized Mechanisms (diagnostic only)

- Dominant gate `g17_status` drives most lane fails in current Stage-2 prereg range.
- Joint signatures (e.g. `g17_status+g18_status`) suggest coupled fragility in hard regimes.
- RC concentration indicates estimator sensitivity rather than coupling (G20) instability.

## Notes

- Tooling only; no gate threshold or formula changes.
