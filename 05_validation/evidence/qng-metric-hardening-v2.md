# Evidence - QNG-T-METRIC-002

- Priority: P3
- Claim: QNG-CORE-METRIC-V2
- Claim statement: Dynamic metric from `Hessian(Sigma)` improves signal-vs-random discrimination while preserving metric sanity gates.
- Derivation: `03_math/derivations/qng-core-emergent-metric-v1.md`
- Definition lock: `01_notes/metric/metric-lock-v2.md`
- Pre-registration: `05_validation/pre-registrations/qng-metric-hardening-v2.md`
- Evidence file: `05_validation/evidence/qng-metric-hardening-v2.md`
- Current status: fail

## Objective

Run v2 metric method (`g <- SPD_projection(-Hessian(Sigma_s))`) with locked gates D1-D4 and verify whether D4 collapse is recovered without breaking D1-D3.

## Reproducible Run

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v2.py `
  --dataset-id DS-002 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 2401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v2"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| Metric lock | `01_notes/metric/metric-lock-v2.md` (2026-02-21) | Dynamic metric extraction from Sigma Hessian |
| Core derivation | `03_math/derivations/qng-core-emergent-metric-v1.md` (2026-02-21) | Boxed metric/Hessian definitions |
| Prereg gates | `05_validation/pre-registrations/qng-metric-hardening-v2.md` (2026-02-21) | D1-D4 locked |
| Runner | `scripts/run_qng_metric_hardening_v2.py` | Executes v2 checks and controls |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Gate checks | `05_validation/evidence/artifacts/qng-metric-hardening-v2/metric_checks.csv` | Prereg gate results |
| Eigen diagnostics | `05_validation/evidence/artifacts/qng-metric-hardening-v2/eigs.csv` | Local metric eigenvalues |
| Scale drift | `05_validation/evidence/artifacts/qng-metric-hardening-v2/drift.csv` | Relative Frobenius drifts |
| Sigma alignment | `05_validation/evidence/artifacts/qng-metric-hardening-v2/align_sigma.csv` | Raw vs shuffled cosine similarities |
| Config snapshot | `05_validation/evidence/artifacts/qng-metric-hardening-v2/config.json` | Run config and locks |
| Run log | `05_validation/evidence/artifacts/qng-metric-hardening-v2/run-log.txt` | Runtime + artifact hashes |
| Plot (eigs) | `05_validation/evidence/artifacts/qng-metric-hardening-v2/eigs-hist.png` | Min-eigen distribution |
| Plot (drift) | `05_validation/evidence/artifacts/qng-metric-hardening-v2/drift-distribution.png` | Delta_g distribution |
| Plot (cosine) | `05_validation/evidence/artifacts/qng-metric-hardening-v2/cos-sim-distribution.png` | Alignment distribution |

## Gate Results (D1-D4)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| D1 | `min_eig_global` | `5.524646e-05` | `>= 1e-8` | pass |
| D2 | `median(Delta_g)` | `0.461250` | `<= 0.10` | fail |
| D2 | `p90(Delta_g)` | `0.681578` | `<= 0.25` | fail |
| D3 | `median(cos_sim)` | `0.945517` | `>= 0.90` | pass |
| D3 | `p10(cos_sim)` | `0.556988` | `>= 0.70` | fail |
| D4 | `median(cos_sim_shuffled)` | `-0.102081` | `< 0.55` | pass |
| FINAL | Decision | `fail` | `D1&D2&D3&D4` | fail |

## Decision

- Decision: fail
- Rationale:
  - D4 objective is achieved (shuffle collapse now present), matching v2 target.
  - D1 is repaired (SPD now valid).
  - Remaining blockers are D2 scale-stability and D3 lower-tail robustness.
  - Gates remain unchanged; any further method changes require v3 prereg.

## Interpretation Class

- Validated in pipeline: no
- Validated on REAL data: no
- Suggestive: yes (D4 and D1 improvements)
- Speculative: yes (until D2 and D3 both pass)

