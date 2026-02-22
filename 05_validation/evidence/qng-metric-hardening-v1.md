# Evidence - QNG-T-METRIC-001

- Priority: P3
- Claim: QNG-CORE-METRIC-V1
- Claim statement: Coarse-grained graph distance yields an emergent continuous metric compatible with Sigma gradients and GR-limit sanity.
- Derivation: `03_math/derivations/qng-core-emergent-metric-v1.md`
- Definition lock: `01_notes/metric/metric-lock-v1.md`
- Pre-registration: `05_validation/pre-registrations/qng-metric-hardening-v1.md`
- Evidence file: `05_validation/evidence/qng-metric-hardening-v1.md`
- Current status: fail

## Objective

Audit emergent metric extraction under locked v1 definitions with preregistered gates:
- D1 SPD/signature
- D2 coarse-grain stability
- D3 Sigma compatibility
- D4 negative-control collapse

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v1.py `
  --dataset-id DS-002 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 1401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v1"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| Metric lock | `01_notes/metric/metric-lock-v1.md` (2026-02-21) | Fixed definitions, scales, chart, sampling, normalization |
| Core derivation | `03_math/derivations/qng-core-emergent-metric-v1.md` (2026-02-21) | Boxed metric definition + Hessian estimator |
| Prereg gates | `05_validation/pre-registrations/qng-metric-hardening-v1.md` (2026-02-21) | D1-D4 locked |
| Runner | `scripts/run_qng_metric_hardening_v1.py` | Executes all checks and control |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Gate checks | `05_validation/evidence/artifacts/qng-metric-hardening-v1/metric_checks.csv` | Prereg gate results |
| Eigen diagnostics | `05_validation/evidence/artifacts/qng-metric-hardening-v1/eigs.csv` | Local metric eigenvalues by anchor/scale |
| Scale drift | `05_validation/evidence/artifacts/qng-metric-hardening-v1/drift.csv` | Relative Frobenius drifts |
| Sigma alignment | `05_validation/evidence/artifacts/qng-metric-hardening-v1/align_sigma.csv` | Raw vs shuffled cosine similarities |
| Config snapshot | `05_validation/evidence/artifacts/qng-metric-hardening-v1/config.json` | Run config and locks |
| Run log | `05_validation/evidence/artifacts/qng-metric-hardening-v1/run-log.txt` | Runtime + artifact hashes |
| Plot (eigs) | `05_validation/evidence/artifacts/qng-metric-hardening-v1/eigs-hist.png` | Min-eigen distribution |
| Plot (drift) | `05_validation/evidence/artifacts/qng-metric-hardening-v1/drift-distribution.png` | Delta_g distribution |
| Plot (cosine) | `05_validation/evidence/artifacts/qng-metric-hardening-v1/cos-sim-distribution.png` | Alignment distribution |

## Gate Results (D1-D4)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| D1 | `min_eig_global` | `-0.099214` | `>= 1e-8` | fail |
| D2 | `median(Delta_g)` | `0.539130` | `<= 0.10` | fail |
| D2 | `p90(Delta_g)` | `0.730295` | `<= 0.25` | fail |
| D3 | `median(cos_sim)` | `0.989022` | `>= 0.90` | pass |
| D3 | `p10(cos_sim)` | `0.894017` | `>= 0.70` | pass |
| D4 | `median(cos_sim_shuffled)` | `0.990114` | `< 0.55` | fail |
| FINAL | Decision | `fail` | `D1&D2&D3&D4` | fail |

## Decision

- Decision: fail
- Rationale:
  - D1 and D2 fail: metric SPD/stability conditions not met under locked v1.
  - D4 fail: shuffle control did not collapse, so current compatibility signal is not discriminative enough.
  - By prereg stop rules, gates are not modified post-hoc; any method changes require v2 lock/prereg.

## Interpretation Class

- Validated in pipeline: no
- Validated on REAL data: no
- Suggestive: partial (D3 only)
- Speculative: yes (until D1/D2/D4 pass)

