# Pre-Registration - QNG Metric GR Bridge v1

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-005`
- Scope: pipeline-level bridge sanity from emergent metric v3 artifacts to weak-field GR-compatible behavior
- Lock dependencies:
  - `01_notes/metric/metric-lock-v3.md`
  - `03_math/derivations/qng-core-gr-bridge-v1.md`

## Fixed Command

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_gr_bridge_v1.py `
  --artifact-dirs "qng-metric-hardening-v3,qng-metric-hardening-v3-ds003,qng-metric-hardening-v3-ds006" `
  --scale-ref "1s0" `
  --out-dir "05_validation/evidence/artifacts/qng-metric-gr-bridge-v1"
```

## Inputs (Locked)

- artifact bundles:
  - `05_validation/evidence/artifacts/qng-metric-hardening-v3`
  - `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003`
  - `05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006`
- files required per bundle:
  - `eigs.csv`
  - `align_sigma.csv`
  - `drift.csv`
  - `metric_checks.csv`
- reference scale for weak-field checks:
  - `1s0`

## Gates (Locked)

### B1 - Weak-Field Perturbation

From `h_ij = g_ij - (1/2)delta_ij`:

- `median(||h||_F) <= 0.18`
- `p90(||h||_F) <= 0.30`

### B2 - Metric Sanity

- `min_eig_global >= 0.25`
- `p90(cond_number) <= 2.50`

### B3 - Newtonian-Direction Compatibility

- `median(cos_raw) >= 0.95`
- `p10(cos_raw) >= 0.90`

### B4 - Continuum Stability Across Scales

- `median(delta_g_fro_rel) <= 0.07`
- `p90(delta_g_fro_rel) <= 0.20`

### B5 - Control Separation

- `median(cos_raw) - median(cos_shuffled) >= 0.90`

## Final Decision

- Pass only if all `B1..B5` pass for all listed datasets.

## Stop Conditions (Anti-Tuning)

- If fail: keep thresholds unchanged.
- Any threshold or metric-definition change requires `qng-metric-gr-bridge-v2.md`.

## Required Outputs

- `dataset_summary.csv`
- `bridge_checks.csv`
- `input_hashes.csv`
- `config.json`
- `summary.md`
- `run-log.txt`
