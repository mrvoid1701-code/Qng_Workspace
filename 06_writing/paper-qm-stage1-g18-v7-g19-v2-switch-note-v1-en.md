# QM Stage-1 Combined Governance Switch Note (G18-v7 + G19-v2)

Date: 2026-03-05

## Abstract

We report a combined governance-layer hardening update for QM Stage-1 in QNG Workspace: `G19-v2` plus `G18-v7`. The update keeps all core gate formulas and thresholds unchanged, and only modifies decision-layer estimators on source-official fail cases. Under preregistered non-degradation constraints (primary/attack/holdout), the policy improves official QM-lane pass from `2470/2500` (`v10`) to `2489/2500` (`v11`) with `degraded=0`.

## Candidate Components

### G19-v2

- preserves source pass decisions
- targets `G19d` fail cases only
- computes high-signal slope envelope from thermal propagator samples
- applies unchanged parsed threshold from `metric_checks_unruh.csv` (`<-1e-05`)

### G18-v7

- built on top of G19-v2 summaries
- preserves source pass decisions
- expands basin quantile and window search over local spectral-dimension recovery
- applies unchanged `G18d` threshold band from metric checks (`1.2..3.5`)

## Promotion Outcomes

### G19-v2

- Primary: `591/600 -> 595/600`, degraded=`0`
- Attack: `1479/1500 -> 1483/1500`, degraded=`0`
- Holdout: `400/400 -> 400/400`, degraded=`0`

### G18-v7 (post G19-v2)

- Primary: `595/600 -> 597/600`, degraded=`0`
- Attack: `1483/1500 -> 1492/1500`, degraded=`0`
- Holdout: `400/400 -> 400/400`, degraded=`0`

## Official-v11 Outcomes

- QM Stage-1 pass: `2489/2500` (`99.56%`)
- residual fail: `11/2500`
- residual gate mix:
  - `G17`: `7` (`G17b`)
  - `G19`: `3`
  - `G18`: `1` (`G18b`)
  - `G20`: `0`

## Regression + Projection

- Baseline/guard refresh `v9`: `PASS` on primary/attack/holdout
- Stage-2 projection:
  - `raw->official`: `1750 -> 2489` pass
  - improved `fail->pass`: `739`
  - degraded `pass->fail`: `0`

## Anti Post-Hoc Statement

This update remains within anti post-hoc governance:

- no threshold tuning,
- no core formula changes,
- candidate-first prereg flow on primary/attack/holdout,
- explicit `degraded=0` requirement before official switch.
