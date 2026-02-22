# Evidence - QNG-T-METRIC-005

- Priority: P3
- Claim: QNG-CORE-METRIC-GR-BRIDGE-V1
- Claim statement: Emergent metric v3 provides a stable weak-field bridge to GR-compatible Newtonian direction in pipeline checks.
- Derivation: `03_math/derivations/qng-core-gr-bridge-v1.md`
- Definition lock: `01_notes/metric/metric-lock-v3.md`
- Pre-registration: `05_validation/pre-registrations/qng-metric-gr-bridge-v1.md`
- Evidence file: `05_validation/evidence/qng-metric-gr-bridge-v1.md`
- Current status: pass

## Objective

Validate an explicit metric-to-GR bridge using locked v3 metric artifacts on DS-002/DS-003/DS-006, without modifying v3 method/gates.

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_gr_bridge_v1.py `
  --artifact-dirs "qng-metric-hardening-v3,qng-metric-hardening-v3-ds003,qng-metric-hardening-v3-ds006" `
  --scale-ref "1s0" `
  --out-dir "05_validation/evidence/artifacts/qng-metric-gr-bridge-v1"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| Bridge derivation | `03_math/derivations/qng-core-gr-bridge-v1.md` (2026-02-21) | Weak-field split + Newtonian-direction bridge |
| Metric lock | `01_notes/metric/metric-lock-v3.md` | Frozen estimator and scales |
| Prereg gates | `05_validation/pre-registrations/qng-metric-gr-bridge-v1.md` | B1-B5 locked |
| Upstream artifacts | `qng-metric-hardening-v3*` bundles | DS-002/003/006 inputs |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Dataset summary | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/dataset_summary.csv` | Per-dataset bridge metrics and gate flags |
| Global checks | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/bridge_checks.csv` | B1-B5 + FINAL |
| Input hashes | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/input_hashes.csv` | Reproducibility hashes of upstream CSV inputs |
| Config snapshot | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/config.json` | Command + thresholds + runtime |
| Summary note | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/summary.md` | Human-readable gate table |
| Run log | `05_validation/evidence/artifacts/qng-metric-gr-bridge-v1/run-log.txt` | Runtime and output inventory |

## Gate Results (Global)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| B1 | weak field `max med/p90 ||h||_F` | `0.147479 / 0.255004` | `med<=0.18`, `p90<=0.30` | pass |
| B2 | sanity `min eig / max cond_p90` | `0.300471 / 2.128081` | `min_eig>=0.25`, `cond_p90<=2.50` | pass |
| B3 | Newton direction `min median/p10 cos_raw` | `0.992374 / 0.951282` | `median>=0.95`, `p10>=0.90` | pass |
| B4 | continuum `max median/p90 drift` | `0.059885 / 0.178355` | `median<=0.07`, `p90<=0.20` | pass |
| B5 | control separation `min(raw_med-shuf_med)` | `1.106037` | `>=0.90` | pass |
| FINAL | decision | `pass` | all B1-B5 pass on all datasets | pass |

## Cross-Dataset Snapshot

| Dataset | B1 | B2 | B3 | B4 | B5 | Final |
| --- | --- | --- | --- | --- | --- | --- |
| DS-002 | pass | pass | pass | pass | pass | pass |
| DS-003 | pass | pass | pass | pass | pass | pass |
| DS-006 | pass | pass | pass | pass | pass | pass |

## Decision

- Decision: pass
- Rationale: all prereg bridge gates pass on all three locked v3 datasets with unchanged method inputs.

## Interpretation Class

- Validated in pipeline: yes
- Validated on REAL data: no
- Suggestive: yes
- Speculative: no (for pipeline-level statement)
