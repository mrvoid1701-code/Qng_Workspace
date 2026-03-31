# QM Stage-2 G17 Candidate (v1) - Pre-registration

Date: 2026-03-04  
Status: candidate-only lane (no official switch in this prereg)

## Motivation

Stage-2 strict taxonomy (`qm-stage2-failure-taxonomy-v1`) shows `g17_status` as the dominant fail gate in the prereg blocks.

This prereg defines a focused candidate iteration for `G17` only, before touching coupled `G18` logic.

## Frozen Inputs

- Primary: `DS-002,DS-003,DS-006`, seeds `3401..3600`
- Attack: `DS-002,DS-003,DS-006`, seeds `3601..4100`
- Holdout: `DS-004,DS-008`, seeds `3401..3600`
- Coupling reference must remain:
  - `qm-gr-coupling-audit-v2/bundle-v1` overall `PASS`
  - `g20_pass=2500/2500`, GR guard pre/post pass

## Candidate Scope

- Modify only `G17` candidate estimator lane.
- Keep `G18/G19/G20` definitions unchanged in official lane.
- No threshold tuning in official policy files.

## Evaluation Protocol

Run candidate and compare against current Stage-2 prereg lane:

1. Primary block comparison
2. Attack block comparison
3. Holdout block comparison

## Promotion Criteria (must all hold)

1. `degraded=0` on `all_pass_qm_lane` counts per block.
2. Net uplift on primary block fail count.
3. Non-degradation on holdout block.
4. Coupling checks remain stable (`G20`, GR guard pre/post).

## Governance Rule

- If criteria pass: open governance switch proposal as separate commit.
- If criteria fail: keep as candidate-only and document failure taxonomy delta.

## Anti Post-Hoc Guard

- No edits to thresholds/formulas after seeing evaluation outcomes.
- Any further changes require a new prereg revision (`v2`).
