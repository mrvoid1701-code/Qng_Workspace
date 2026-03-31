# QM Stage-1 Note: G18-v3 Official Switch (v1)

Date: 2026-03-04

## Abstract

This note records a governance-layer upgrade of QM Stage-1 where G18-v3 replaces G18-v2 as official decision policy, while preserving G17-v3 from the prior official version. No gate formulas or thresholds were changed.

## Method

The candidate-v3 policy generalized local spectral-dimension recovery for G18d failures while preserving all legacy passes (`degraded=0` by construction and validated in promotion reports).

Promotion was evaluated on prereg blocks:

- primary: `DS-002/003/006`, seeds `3401..3600`
- attack: `DS-002/003/006`, seeds `3601..4100`
- holdout: `DS-004/008`, seeds `3401..3600`

## Results

Across all blocks, promotion checks passed:

- primary lane: `513/600 -> 529/600`
- attack lane: `1255/1500 -> 1316/1500`
- holdout lane: `360/400 -> 372/400`
- `degraded=0` in each block

Post-switch taxonomy improved from `372/2500` fails (`14.88%`) to `283/2500` (`11.32%`), i.e. `-89` fail profiles.

## Interpretation

Residual QM Stage-1 failures remain concentrated in G18/G17 diagnostics rather than coupling closure (`G20` remains stable). This keeps the project in a clean anti-post-hoc state: stronger pass rates from observable-definition hardening, not threshold relaxation.

## Conclusion

The switch to `qm-stage1-g18-v3-official` is justified by prereg uplift and zero degradation, and is now protected by a refreshed baseline/guard package (`qm-stage1-regression-baseline-v3`, `PASS`).
