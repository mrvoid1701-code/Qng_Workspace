# Evidence - Core Closure v1 (Node + Volume + Chi)

- Scope date: 2026-02-21
- Related claims: `QNG-C-029`, `QNG-C-032`, `QNG-C-103`, `QNG-C-104`
- Closure note: `01_notes/core-closure-v1.md`
- Runner: `scripts/run_qng_t_v_volume_rules.py`

## Objective

Select and freeze one v1 volume rule with explicit, reproducible closure gates:
- `T-V-01` conservation/growth gate
- `T-V-02` spectrum gate
- `T-V-03` attractor/identity gate
- `T-V-04` GR-limit kill switch

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_v_volume_rules.py `
  --dataset-id DS-002 `
  --steps 180 `
  --runs 12 `
  --seed 920 `
  --out-dir "05_validation/evidence/artifacts/qng-tv-core-closure-v1"
```

## Outputs

- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/rule-comparison.csv`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/robustness-runs.csv`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/parameter-stability.md`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/stationarity-windows.csv`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/volume-rules-timeseries.png`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/run-log.txt`

## Result

- `V-A`: fail (does not satisfy growth/spectrum gate policy)
- `V-B`: pass (all four gates pass at `1.0` pass-rate in this batch)
- `selected_rule_v1`: `V-B`

## Decision

Core closure v1 is frozen with `V-B` as the operational volume rule for subsequent tests.

