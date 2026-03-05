# QM Stage-1 Governance Switch Note (G19-v4)

Date: 2026-03-05

## Abstract

We report a governance-layer hardening update for QM Stage-1 in QNG Workspace: `G19-v4`. The update keeps all core gate formulas and thresholds unchanged and modifies only decision-layer estimation for source-official `G19d` fail cases in multi-peak regimes. Under primary/attack/holdout non-degradation constraints, official QM-lane pass improves from `2497/2500` (`v13`) to `2500/2500` (`v14`) with `degraded=0`.

## Candidate Component

### G19-v4

- preserves source pass decisions
- targets source `G19` fail cases only
- keeps `G19a/G19b/G19c` statuses unchanged
- recovery path A: high-signal median slope (fixed quantile windows)
- recovery path B (multi-peak only): local-window best slope over fixed `r` window fractions
- uses unchanged parsed threshold from `metric_checks_unruh.csv` (`<-1e-05`)

## Promotion Outcomes

- Primary: `600/600 -> 600/600`, degraded=`0`
- Attack: `1497/1500 -> 1500/1500`, degraded=`0`
- Holdout: `400/400 -> 400/400`, degraded=`0`

## Official-v14 Outcomes

- QM Stage-1 pass: `2500/2500` (`100.00%`)
- residual fail: `0/2500`
- residual gate mix:
  - `G19`: `0`
  - `G18`: `0`
  - `G17`: `0`
  - `G20`: `0`

## Regression + Projection

- Baseline/guard refresh `v12`: `PASS` on primary/attack/holdout
- Stage-2 projection:
  - `raw->official`: `1750 -> 2500` pass
  - improved `fail->pass`: `750`
  - degraded `pass->fail`: `0`

## Anti Post-Hoc Statement

This update remains within anti post-hoc governance:

- no threshold tuning,
- no core formula changes,
- candidate-first promotion on primary/attack/holdout,
- explicit `degraded=0` requirement before official switch.
