# D4 Winner Objective Forensics v1

Forensics-only comparison across strict winner lanes (no threshold/formula changes).

- generated_utc: `2026-03-10T07:06:20.965869+00:00`
- lanes: `v10, v11, v12`
- best lane by pass_count: `v10` (4/5)
- persistent hold seeds across all lanes: `3403`

## Dominant Failure Signature
- top failing check: `check_generalization_gap_ok` (count=5)

## Interpretation
- If the same seed remains HOLD across objective variants, the blocker is likely split-regime sensitivity (distribution shift), not optimizer noise.
- Recommended next step: keep strict lane frozen and add a separate stratified-split methodological lane.
