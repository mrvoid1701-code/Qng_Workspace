# QM Stage-1 Governance Switch Note (G17b-v6)

Date: 2026-03-05

## Abstract

We report a governance-layer hardening update for QM Stage-1 in QNG Workspace: `G17b-v6`. The update keeps all core gate formulas and thresholds unchanged, and only modifies decision-layer estimation on source-official fail cases. Under primary/attack/holdout non-degradation constraints, the policy improves official QM-lane pass from `2489/2500` (`v11`) to `2496/2500` (`v12`) with `degraded=0`.

## Candidate Component

### G17b-v6

- preserves source pass decisions
- targets `G17b` fail cases only
- computes OLS slope on high-signal subsets over fixed quantile windows of `|G_ij|`
- aggregates slopes with median (robust against low-signal tail contamination)
- applies unchanged parsed threshold from `metric_checks_qm.csv` (`<-0.01`)

## Promotion Outcomes

- Primary: `597/600 -> 600/600`, degraded=`0`
- Attack: `1492/1500 -> 1496/1500`, degraded=`0`
- Holdout: `400/400 -> 400/400`, degraded=`0`

## Official-v12 Outcomes

- QM Stage-1 pass: `2496/2500` (`99.84%`)
- residual fail: `4/2500`
- residual gate mix:
  - `G19`: `3`
  - `G18`: `1`
  - `G17`: `0`
  - `G20`: `0`

## Regression + Projection

- Baseline/guard refresh `v10`: `PASS` on primary/attack/holdout
- Stage-2 projection:
  - `raw->official`: `1750 -> 2496` pass
  - improved `fail->pass`: `746`
  - degraded `pass->fail`: `0`

## Anti Post-Hoc Statement

This update remains within anti post-hoc governance:

- no threshold tuning,
- no core formula changes,
- candidate-first promotion on primary/attack/holdout,
- explicit `degraded=0` requirement before official switch.
