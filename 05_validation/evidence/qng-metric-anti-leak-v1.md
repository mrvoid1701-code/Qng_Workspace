# Evidence - QNG-T-METRIC-004

- Priority: P3
- Claim: QNG-CORE-METRIC-V3-CONTROL
- Claim statement: Metric v3 remains discriminative under anti-leak controls (label permutation and graph rewiring).
- Base derivation: `03_math/derivations/qng-core-emergent-metric-v1.md`
- Base lock: `01_notes/metric/metric-lock-v3.md`
- Pre-registration: `05_validation/pre-registrations/qng-metric-anti-leak-v1.md`
- Evidence file: `05_validation/evidence/qng-metric-anti-leak-v1.md`
- Current status: pass (stable across DS-002, DS-003, DS-006)

## Objective

Add an explicit anti-leak / anti-shortcut control layer beyond D4:
- label permutation control
- graph rewiring control
- graph rewiring + label permutation control

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_anti_leak_v1.py `
  --dataset-id DS-002 `
  --samples 72 `
  --seed 3401 `
  --rewire-runs 12 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1"
```

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Control summary | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1/control_summary.csv` | Final anti-leak metrics + pass flags |
| Rewire runs | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1/rewire_runs.csv` | Per-run rewiring outcomes |
| Config snapshot | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1/config.json` | Run config |
| Run log | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1/run-log.txt` | Runtime + hashes |
| Hashes | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1/artifact-hashes.json` | Auditability |
| DS-003 summary | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds003/control_summary.csv` | Cross-dataset anti-leak replication |
| DS-006 summary | `05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds006/control_summary.csv` | Cross-dataset anti-leak replication |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `positive_median_cos` | `0.992374` | reference | pass |
| `label_perm_median_cos` | `0.242666` | `< 0.55` | pass |
| `rewire_median_of_medians` | `0.036314` | `< 0.55` | pass |
| `rewire_shuffled_median_of_medians` | `-0.068478` | `< 0.55` | pass |
| `overall_pass` | `True` | all controls pass | pass |

## Cross-Dataset Anti-Leak Replication

| Dataset | positive_median | label_perm_median | rewire_median | rewire_shuffled_median | Final |
| --- | --- | --- | --- | --- | --- |
| `DS-002` | `0.992374` | `0.242666` | `0.036314` | `-0.068478` | pass |
| `DS-003` | `0.994201` | `0.143302` | `0.036521` | `-0.015755` | pass |
| `DS-006` | `0.995345` | `0.022733` | `-0.119704` | `-0.033509` | pass |

## Decision

- Decision: pass
- Rationale: all anti-leak controls collapse as expected, including cross-dataset runs, adding an explicit graph-structure shortcut check on top of existing D4.
- Last updated: 2026-02-21
- Authenticity: silver
- Leakage risk: low
- Negative control: done

## Calibration vs Holdout (No-Double-Dipping Declaration)

- **Calibration set:** DS-002 — anti-leak control thresholds (`< 0.55`) were locked in prereg before any run.
- **Holdout sets:** DS-003, DS-006 — run with identical thresholds and identical control types after DS-002 pass. No threshold edits between datasets.
- **Tuning:** no control parameters were tuned post-hoc. The threshold `< 0.55` was set in prereg to be strictly below the positive signal (~0.99), not fitted to control outcomes.
- **Statement:** DS-003 and DS-006 anti-leak results are genuine out-of-sample replications.
