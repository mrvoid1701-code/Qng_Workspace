# D4 Split Shift Diagnostics v1

Forensics-only train/holdout shift audit over fixed split seeds.

- generated_utc: `2026-03-10T07:09:28.087253+00:00`
- dataset_id: `DS-006`
- split_seeds: `3401,3402,3403,3404,3405`
- top shift seed: `3402` (score=0.778017)
- seed 3403 shift rank: `2`
- corr(split_shift_score, v10_generalization_gap_pp): `-0.146404`

## Signal
- `split_shift_score = |delta_low_accel_outer_frac| + |delta_mean_log10_gbar| + 0.05*|delta_p90_r|`
- Higher score indicates stronger distribution mismatch between train and holdout.
- If correlation vs gap is weak, global split-shift is not sufficient to explain HOLD behavior.
