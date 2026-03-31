# QM Stage-1 Governance Switch Note (G18b-v8)

Date: 2026-03-05

## Abstract

We report a governance-layer hardening update for QM Stage-1 in QNG Workspace: `G18b-v8`. The update keeps all core gate formulas and thresholds unchanged, and only modifies decision-layer estimation on source-official `G18b` fail cases. Under primary/attack/holdout non-degradation constraints, official QM-lane pass improves from `2496/2500` (`v12`) to `2497/2500` (`v13`) with `degraded=0`.

## Candidate Component

### G18b-v8

- preserves source pass decisions
- targets `G18b` fail cases only
- recomputes `n*IPR` by trimmed mean over mode-level `n_IPR_k`
- uses unchanged parsed threshold from `metric_checks_qm_info.csv` (`<5.0`)
- preserves source `G18d-v2` status and does not alter `G18d` logic

## Promotion Outcomes

- Primary: `600/600 -> 600/600`, degraded=`0`
- Attack: `1496/1500 -> 1497/1500`, degraded=`0`
- Holdout: `400/400 -> 400/400`, degraded=`0`

## Official-v13 Outcomes

- QM Stage-1 pass: `2497/2500` (`99.88%`)
- residual fail: `3/2500`
- residual gate mix:
  - `G19`: `3`
  - `G18`: `0`
  - `G17`: `0`
  - `G20`: `0`

## Regression + Projection

- Baseline/guard refresh `v11`: `PASS` on primary/attack/holdout
- Stage-2 projection:
  - `raw->official`: `1750 -> 2497` pass
  - improved `fail->pass`: `747`
  - degraded `pass->fail`: `0`

## Anti Post-Hoc Statement

This update remains within anti post-hoc governance:

- no threshold tuning,
- no core formula changes,
- candidate-first promotion on primary/attack/holdout,
- explicit `degraded=0` requirement before official switch.
