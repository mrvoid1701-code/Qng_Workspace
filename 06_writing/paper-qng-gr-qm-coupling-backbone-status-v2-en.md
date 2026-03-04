# QNG GR-QM Coupling Backbone and Remaining Failure Structure (Status Note v2)

Date: 2026-03-04

## Abstract

We report a reproducibility-focused checkpoint for the QNG GR-QM pipeline. The semiclassical coupling lane now has a complete and resumable evidence bundle over 2500 profiles (primary, attack, holdout), with full G20 pass and no GR guard degradation pre/post coupling. GR Stage-3 remains at 597/600 with three isolated G11 edge-case failures. QM Stage-2 remains a HOLD lane, with failure taxonomy indicating G17 as the dominant gate-level contributor.

## Coupling Backbone

A bundled coupling package confirms:

- completed profiles: 2500/2500
- G20 pass: 2500/2500
- GR guard pre: PASS
- GR guard post: PASS

This supports the operational claim that the current QM coupling path does not destabilize the frozen GR baseline in the tested regime.

## GR Residual Risk

GR Stage-3 official remains 597/600. The remaining three failures are all in G11 and are isolated under local seed-neighborhood checks (+/-5), suggesting edge-case estimator sensitivity rather than global instability.

## QM Stage-2 Failure Structure

Stage-2 prereg taxonomy over 2500 profiles reports 750 failures (30.0%), with dominant signatures:

- G17-only
- G18-only
- G17+G18 coupled fails

Thus, the next scientifically clean step is candidate-lane estimator hardening centered on G17 first, then the coupled G18 subset, under prereg + degraded=0 governance.

## Conclusion

The project currently has a strong coupling backbone and reproducibility posture. The remaining work is concentrated in defined estimator fragility zones, not in broad pipeline instability.
