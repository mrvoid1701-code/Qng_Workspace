# QNG-T-METRIC-006 — GR Bridge v2 (Frobenius iso = 1/sqrt(2))

- Date: 2026-02-24
- Datasets: DS-002, DS-003, DS-006 (v4 metric artifacts)
- Runner: `scripts/run_qng_metric_gr_bridge_v2.py`
- Out dir: `05_validation/evidence/artifacts/qng-metric-gr-bridge-v2/`
- Iso reference: 0.707107 (Frobenius isotropic target for v4)

## Gate results (global)
- B1 weak-field h_norm med/p90: 0.1904 / 0.2869 (thr 0.20 / 0.32) → pass
- B2 metric sanity: min_eig=0.4247; cond_p90=1.8513 (thr min_eig≥0.25; cond≤2.50) → pass
- B3 Newton direction: cos_raw med/p10 = 0.9933 / 0.9638 (thr 0.95 / 0.90) → pass
- B4 continuum stability: drift med/p90 = 0.0525 / 0.1444 (thr 0.07 / 0.20) → pass
- B5 control separation: raw-shuf gap min = 1.0985 (thr ≥0.90) → pass
- FINAL: pass

## Per-dataset summary (dataset_summary.csv)

| dataset | h_med | h_p90 | min_eig | cond_p90 | cos_med | cos_p10 | drift_med | drift_p90 | gap_raw_shuf | pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 0.1705 | 0.2777 | 0.4251 | 1.8513 | 0.9944 | 0.9711 | 0.0508 | 0.1436 | 1.0985 | True |
| DS-003 | 0.1904 | 0.2869 | 0.4247 | 1.8513 | 0.9933 | 0.9638 | 0.0525 | 0.1444 | 1.0985 | True |
| DS-006 | 0.1824 | 0.2862 | 0.4249 | 1.8513 | 0.9941 | 0.9653 | 0.0537 | 0.1444 | 1.0985 | True |

## Required files checked
- `metric_checks.csv`, `eigs.csv`, `align_sigma.csv`, `drift.csv` for each artifact dir.
- Hashes recorded in `input_hashes.csv`.

## Repro command
```
python scripts/run_qng_metric_gr_bridge_v2.py \
  --artifact-dirs "qng-metric-hardening-v4-ds002,qng-metric-hardening-v4-ds003,qng-metric-hardening-v4-ds006" \
  --out-dir "05_validation/evidence/artifacts/qng-metric-gr-bridge-v2"
```
