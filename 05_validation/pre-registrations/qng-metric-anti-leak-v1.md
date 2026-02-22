# Pre-Registration - QNG Metric Anti-Leak Controls v1

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-004`
- Scope: supplementary anti-leak / anti-shortcut controls for `QNG-CORE-METRIC-V3`
- Lock dependencies:
  - `01_notes/metric/metric-lock-v3.md`
  - `05_validation/pre-registrations/qng-metric-hardening-v3.md`
  - `scripts/run_qng_metric_anti_leak_v1.py`

## Fixed Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_anti_leak_v1.py `
  --dataset-id DS-002 `
  --samples 72 `
  --seed 3401 `
  --rewire-runs 12 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1"
```

## Controls (Locked)

### C1 - Label Permutation Control

- Permute `Sigma` labels on base graph.
- Compare metric-driven direction against base raw direction.
- Pass: `median_cos < 0.55`.

### C2 - Graph Rewire Control

- Degree-preserving rewiring on graph edges.
- Compare rewired metric-driven direction against raw direction from original/base graph.
- Pass: `median_of_run_medians < 0.55`.

### C3 - Graph Rewire + Label Permutation Control

- Rewired graph + permuted `Sigma`.
- Same comparator against base raw direction.
- Pass: `median_of_run_medians < 0.55`.

## Stop Conditions (Anti-Tuning)

- No edits to `metric-lock-v3` and no D1-D4 threshold changes.
- Any method change requires `qng-metric-anti-leak-v2.md`.

## Output Requirement

Required artifacts:
- `control_summary.csv`
- `rewire_runs.csv`
- `config.json`
- `run-log.txt`

