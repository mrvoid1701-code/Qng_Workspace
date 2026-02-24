# Evidence - QNG-T-METRIC-003

- Priority: P3
- Claim: QNG-CORE-METRIC-V3
- Claim statement: Dynamic metric from `Hessian(Sigma)` with conformal gauge normalization and fixed anisotropy shrinkage should satisfy full prereg metric hardening gates.
- Derivation: `03_math/derivations/qng-core-emergent-metric-v1.md`
- Definition lock: `01_notes/metric/metric-lock-v3.md`
- Pre-registration: `05_validation/pre-registrations/qng-metric-hardening-v3.md`
- Evidence file: `05_validation/evidence/qng-metric-hardening-v3.md`
- Current status: pass (stable across DS-002, DS-003, DS-006)

## Objective

Run v3 metric method (`g <- shrink(trace-normalized(SPD_projection(-Hessian(Sigma_s))))`) with locked gates D1-D4 and verify full prereg pass without gate edits.

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py `
  --dataset-id DS-002 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 3401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3"
```

Cross-dataset replication (same lock, same gates, no method edits):

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py `
  --dataset-id DS-003 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 3401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003"

.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py `
  --dataset-id DS-006 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 3401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| Metric lock | `01_notes/metric/metric-lock-v3.md` (2026-02-21) | Dynamic Hessian metric with conformal gauge + anisotropy keep `k=0.4` |
| Core derivation | `03_math/derivations/qng-core-emergent-metric-v1.md` (2026-02-21) | Boxed metric/Hessian definitions |
| Prereg gates | `05_validation/pre-registrations/qng-metric-hardening-v3.md` (2026-02-21) | D1-D4 locked |
| Runner | `scripts/run_qng_metric_hardening_v3.py` | Executes v3 checks and controls |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Gate checks | `05_validation/evidence/artifacts/qng-metric-hardening-v3/metric_checks.csv` | Prereg gate results |
| Eigen diagnostics | `05_validation/evidence/artifacts/qng-metric-hardening-v3/eigs.csv` | Local metric eigenvalues |
| Scale drift | `05_validation/evidence/artifacts/qng-metric-hardening-v3/drift.csv` | Relative Frobenius drifts |
| Sigma alignment | `05_validation/evidence/artifacts/qng-metric-hardening-v3/align_sigma.csv` | Raw vs shuffled cosine similarities |
| Config snapshot | `05_validation/evidence/artifacts/qng-metric-hardening-v3/config.json` | Run config and locks |
| Run log | `05_validation/evidence/artifacts/qng-metric-hardening-v3/run-log.txt` | Runtime + artifact hashes |
| Plot (eigs) | `05_validation/evidence/artifacts/qng-metric-hardening-v3/eigs-hist.png` | Min-eigen distribution |
| Plot (drift) | `05_validation/evidence/artifacts/qng-metric-hardening-v3/drift-distribution.png` | Delta_g distribution |
| Plot (cosine) | `05_validation/evidence/artifacts/qng-metric-hardening-v3/cos-sim-distribution.png` | Alignment distribution |
| DS-003 checks | `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003/metric_checks.csv` | Cross-dataset replication (unchanged lock/gates) |
| DS-006 checks | `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/metric_checks.csv` | Cross-dataset replication (unchanged lock/gates) |

## Gate Results (D1-D4)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| D1 | `min_eig_global` | `0.300856` | `>= 1e-8` | pass |
| D2 | `median(Delta_g)` | `0.056367` | `<= 0.10` | pass |
| D2 | `p90(Delta_g)` | `0.178355` | `<= 0.25` | pass |
| D3 | `median(cos_sim)` | `0.992374` | `>= 0.90` | pass |
| D3 | `p10(cos_sim)` | `0.960620` | `>= 0.70` | pass |
| D4 | `median(cos_sim_shuffled)` | `-0.133569` | `< 0.55` | pass |
| FINAL | Decision | `pass` | `D1&D2&D3&D4` | pass |

## Cross-Dataset Replication (Locked v3)

| Dataset | D1 min_eig | D2 median/p90 | D3 median/p10 | D4 shuffled median | Final |
| --- | --- | --- | --- | --- | --- |
| `DS-002` | `0.300856` | `0.056367 / 0.178355` | `0.992374 / 0.960620` | `-0.133569` | pass |
| `DS-003` | `0.300461` | `0.048771 / 0.149748` | `0.994201 / 0.951281` | `-0.111837` | pass |
| `DS-006` | `0.300471` | `0.059885 / 0.139852` | `0.995345 / 0.959466` | `-0.430659` | pass |

## Decision

- Decision: pass
- Rationale:
  - D1 SPD gate remains satisfied with large safety margin.
  - D2 coarse-grain drift is below both prereg thresholds.
  - D3 alignment passes including lower-tail robustness.
  - D4 negative-control collapse remains strong.
  - Unchanged lock/gates replicate pass on DS-003 and DS-006, so closure is promoted to stable at pipeline level.

## Interpretation Class

- Validated in pipeline: yes
- Validated on REAL data: no
- Suggestive: yes
- Speculative: no (for pipeline-level statement)

## Calibration vs Holdout (No-Double-Dipping Declaration)

- **Calibration set:** DS-002 — used to develop and select v3 metric method (Hessian + conformal gauge + anisotropy shrinkage k=0.4). Gates D1-D4 were fixed on this dataset before cross-dataset runs.
- **Holdout sets:** DS-003, DS-006 — run with unchanged lock and unchanged gates after DS-002 pass. No method edits were made between DS-002 and DS-003/DS-006 runs.
- **Tuning:** anisotropy shrinkage `k=0.4` was selected in metric-lock-v3 before this prereg was locked. It is not tuned post-hoc.
- **Locked gates:** D1-D4 thresholds are identical across all three datasets. No per-dataset threshold adjustment was made.
- **Statement:** DS-003 and DS-006 results are genuine out-of-sample replications, not calibration outcomes.
