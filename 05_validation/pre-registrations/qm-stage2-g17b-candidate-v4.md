# QM Stage-2 G17b Candidate (v4) - Pre-registration

Date: 2026-03-04  
Status: candidate-only lane (no official switch in this prereg)

## Motivation

Targeted taxonomy (`qm-stage1-g17b-failure-taxonomy-v1`) over frozen official-v5 scope shows:

- `G17b` fails are concentrated in `DS-006` (`115/700`)
- dominant class is `isolated_near_threshold` (`107/115`)
- coupled co-fails are minority (`7/115`)

This prereg defines a focused `G17b` candidate lane to test estimator hardening without changing gate thresholds.

## Frozen Inputs

- Primary: `DS-002,DS-003,DS-006`, seeds `3401..3600`
- Attack: `DS-002,DS-003,DS-006`, seeds `3601..4100`
- Holdout: `DS-004,DS-008`, seeds `3401..3600`
- Baseline official reference:
  - `qm-stage1-official-v5/*/summary.csv`
- Coupling reference must remain:
  - `qm-gr-coupling-audit-v2/bundle-v1` overall `PASS`
  - `g20_pass=2500/2500`, GR guard pre/post pass

## Candidate Scope

- Modify only candidate logic for `G17b` evaluation lane.
- Keep official `G17/G18/G19/G20` policy and thresholds unchanged.
- Keep core physics formulas unchanged.

## Evaluation Protocol

For each block (primary/attack/holdout):

1. Run candidate summaries.
2. Compare against frozen official-v5 reference.
3. Emit transition report with:
   - improved (`fail->pass`)
   - degraded (`pass->fail`)
   - per-dataset deltas

## Promotion Criteria (must all hold)

1. `degraded=0` on each block.
2. Net uplift on primary block.
3. Non-degradation on holdout block.
4. `DS-006` fail count decreases vs official-v5.
5. Coupling checks remain stable (`G20` + GR guard pre/post unchanged).

## Governance Rule

- If criteria pass: open governance switch proposal in a separate commit.
- If criteria fail: keep candidate-only and publish taxonomy delta.

## Anti Post-Hoc Guard

- No threshold tuning after seeing outcomes.
- If estimator definition changes again, create new prereg revision (`v5`).
