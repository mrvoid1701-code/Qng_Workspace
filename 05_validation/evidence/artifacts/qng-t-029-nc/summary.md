# QNG-T-029-NC - Negative Control Summary

**Date:** 2026-03-15
**Overall result:** PARTIAL (2/4 NCs pass; methodological limitation documented)

## Purpose

Demonstrate that the T-029 positive result (memory kernel improves N-body
structure metrics) is specific to the correct causal exponential kernel (tau=1.3, k=0.85).
Four negative controls are tested; all must show chi2_NC / chi2_correct > 5x.

## Negative Controls

| NC | Description | Seeds passing gate | Mean chi2_NC/chi2_correct | Gate |
|----|----|----|----|----|
| NC-1_tau0 | tau=0 (instantaneous gravity, no memory) | 12/12 seeds | 1334.4x | PASS |
| NC-2_tau_short | tau=0.2 (6.5x too short) | 10/12 seeds | 48.4x | FAIL |
| NC-3_tau_long | tau=8.0 (6x too long) | 0/12 seeds | 1.9x | FAIL |
| NC-4_wrongsign | Negative kernel (anti-gravity memory) | 12/12 seeds | 1364.7x | PASS |

## Reference (T-029 Positive Result)

| Model | total_delta_chi2 | Verdict |
|-------|---------|---------|
| Memory kernel (tau=1.3, k=0.85) | -671.49 | PASS (large improvement over tau=0) |

## Interpretation

**NC-1 (PASS):** tau=0 (instantaneous) produces cluster positions 1000-3000x worse
than the correct causal kernel. Memory is essential.

**NC-2 (FAIL - observable limitation):** tau=0.2 gives mean ratio 48x but 2/12 seeds
fail gate (chi2_correct outliers at seeds 730, 734). Gate fails on consistency.

**NC-3 (FAIL - observable limitation):** tau=8.0 produces equilibrium positions only
1.2-2.9x worse. Longer tau converges to a similar equilibrium attractor because the
integrated potential is approximately preserved. The equilibrium chi2 metric is
insensitive to tau within a factor ~6x.

**NC-4 (PASS):** Negative kernel (anti-gravity) produces 600-3400x worse cluster
positions. Correct sign is essential.

## Methodological Finding

Equilibrium chi2 discriminates memory presence and sign, but not tau timescale.
Trajectory-based chi2 (all timesteps) required for tau specificity.

## Evidence Assessment for C-062

Bronze-plus: memory and correct sign demonstrated necessary (NC-1, NC-4 strong at
1000-1400x). Tau-specificity requires trajectory observable (next step).
