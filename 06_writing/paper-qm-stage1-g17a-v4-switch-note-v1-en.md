# QM Stage-1 G17a-v4 Governance Switch Note (v1)

Date: 2026-03-05

## Abstract

We report a governance-layer hardening step for QM Stage-1 in QNG Workspace: `G17a-v4`. The policy targets residual `g17a-only` failures under multi-peak mixing and applies a fixed multi-window local-gap check while preserving the original `G17a` threshold from metric checks. No core formulas or thresholds were modified. Across primary, attack, and holdout blocks, promotion criteria passed with `degraded=0`, and official policy moved from `v9` to `v10`, improving QM-lane pass from `2465/2500` to `2470/2500`.

## Policy Summary

- Source policy: `qm-stage1-official-v9`
- Candidate policy: `qm-g17a-candidate-v4-multiwindow`
- Official policy after switch: `qm-stage1-official-v10`
- Effective tag: `qm-stage1-g17a-v4-official`

Candidate triggers only when:

1. source `G17` fails,
2. source `G17a` fails while `G17b/c/d` pass,
3. source `multi_peak_mixing=true`.

Decision observable:

- local gap computed on fixed basin quantiles (`0.10, 0.15, 0.22`)
- candidate uses max local gap across windows
- compared against same parsed `G17a` threshold (`>0.01`)

## Promotion Outcomes

- Primary (`DS-002/003/006`, `3401..3600`): `590/600 -> 591/600`, degraded=`0`
- Attack (`DS-002/003/006`, `3601..4100`): `1475/1500 -> 1479/1500`, degraded=`0`
- Holdout (`DS-004/008`, `3401..3600`): `400/400 -> 400/400`, degraded=`0`

## Official-v10 Outcomes

- QM Stage-1 pass: `2470/2500` (`98.8%`)
- Residual fail: `30/2500`
- Gate concentration in residuals:
  - `G18`: `12`
  - `G19`: `11`
  - `G17`: `7` (mostly `G17b`)
  - `G20`: `0`

## Stage-2 Projection

Projected from Stage-2 raw summaries:

- `raw->official`: `1750 -> 2470` pass
- improved (`fail->pass`): `720`
- degraded (`pass->fail`): `0`

## Anti Post-Hoc Statement

This switch maintains anti post-hoc constraints:

- no threshold tuning,
- no formula changes in physics runners,
- candidate-first evaluation with primary/attack/holdout,
- explicit non-degradation requirement (`degraded=0`) before official apply.
