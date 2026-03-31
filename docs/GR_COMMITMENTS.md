# GR Physics-Facing Commitments (Frozen)

Date frozen: 2026-03-02
Scope: public-facing interpretation of current GR bridge outputs.

## What We Commit To (Now)

These are the claims we consider supported under the current gate stack and evidence:

1. Weak-field GR-like behavior is the active interpretation scope.
2. PPN-like diagnostics are primary observables for this scope:
   - `gamma` deviation trend (`G15a`)
   - `beta` consistency window (`G15c`)
   - Shapiro proxy behavior (`G15b`, official `v2`)
   - EP proxy stability (`G15d`)
3. Covariant closure checks are part of required evidence:
   - `G10..G14` + action closure (`G16`)
4. Official decision policies are frozen and reproducible:
   - `G15b`: `v2` official, `v1` legacy diagnostic
   - `G16b`: hybrid official (low-signal -> `v2`, high-signal -> `v1`)
5. Stage-2 governance policy is frozen for reproducibility checks:
   - `G11`: official Stage-2 mapping uses `G11a-v4`
   - `G12`: official Stage-2 mapping uses frozen `G12d-v2`
   - switch/criteria records:
     - `docs/GR_STAGE2_OFFICIAL_SWITCH.md` (v2)
     - `docs/GR_STAGE2_G11_V3_OFFICIAL_SWITCH.md` (v3)
     - `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md` (v4)
6. Stage-3 governance policy is frozen for reproducibility checks:
   - `G11`: official Stage-3 mapping uses candidate-v3 decision status
   - `G12`: official Stage-3 mapping uses candidate-v3 decision status
   - `G7/G8/G9`: inherited unchanged from source runs
   - switch/criteria record:
     - `docs/GR_STAGE3_OFFICIAL_SWITCH.md` (v2, historical)
     - `docs/GR_STAGE3_G11G12_V3_OFFICIAL_SWITCH.md` (v3, current)

## What We Explicitly Do NOT Claim Yet

These remain out of official claim scope at this stage:

1. Strong-field GR completeness.
2. Full `3+1` relativistic formulation coverage.
3. Full tensor-mode gravitational-wave completion.
4. Finalized matter coupling beyond current discrete proxy checks.
5. Full equivalence to continuum Einstein dynamics outside validated weak-field envelope.

## Why This Freeze Exists

This document prevents scope drift and post-hoc storytelling.
Any expansion of claim scope (for example, strong-field or full tensor modes) should be done as:

1. a new prereg protocol,
2. with explicit gates/thresholds listed in advance,
3. and with a separate changelog + evidence package.

## Immediate Next Expansion Track

Planned next stage (not yet claimed as validated):

1. strong-field diagnostics,
2. explicit `3+1` structure checks,
3. full tensor-mode validation,
4. then QM bridge extension on top of that frozen GR stage.

Protocol pointer:

- `docs/GR_STAGE2_PREREG.md`
- `docs/GR_STAGE3_PREREG.md`
- `docs/QM_LANE_POLICY.md`
