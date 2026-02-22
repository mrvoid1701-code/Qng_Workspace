# Raport Executie - Metric v3 Cross-Dataset + Rerun Main Tests (2026-02-21)

## Scope executat

1. Rulare lock `v3` neschimbat pe `DS-003` si `DS-006`.
2. Promovare closure metric la `stable` daca trece cross-dataset.
3. Rerun teste principale `trajectory/lensing` cu closure metric consolidat.

## 1) Metric v3 Cross-Dataset

Comenzi executate (fara schimbari de lock/gates):

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py --dataset-id DS-003 --scales "s0,1.25s0,1.5s0" --samples 72 --seed 3401 --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003"
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v3.py --dataset-id DS-006 --scales "s0,1.25s0,1.5s0" --samples 72 --seed 3401 --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006"
```

Rezultat:

- `DS-003`: `PASS` (`D1-D4`)
- `DS-006`: `PASS` (`D1-D4`)

Metrici cheie:

- `DS-003`: `min_eig=0.300461`, `median_delta_g=0.048771`, `p90_delta_g=0.149748`, `median_cos=0.994201`, `p10_cos=0.951281`, `median_cos_shuffled=-0.111837`
- `DS-006`: `min_eig=0.300471`, `median_delta_g=0.059885`, `p90_delta_g=0.139852`, `median_cos=0.995345`, `p10_cos=0.959466`, `median_cos_shuffled=-0.430659`

Concluzie:

- `QNG-CORE-METRIC-V3` promovat la **stable closure (pipeline-level)** pe `DS-002/003/006`.

## 2) Rerun Main Tests

### QNG-T-028 (Trajectory)

Comanda:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_028_trajectory_real.py --test-id QNG-T-028 --dataset-id DS-005 --flyby-csv data/trajectory/flyby_ds005_real.csv --use-pioneer-anchor --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv --out-dir "05_validation/evidence/artifacts/qng-t-028" --seed 20260220
```

Rezultat:

- `PASS` reconfirmat
- `delta_chi2=-5849.361782`, `delta_AIC=-5847.361782`, `delta_BIC=-5847.415871`

### QNG-T-039 (Lensing/Rotation)

Rulat pachetul principal:

- direct run (`cluster_offsets_real`)
- strict sweeps (`strict3/4/5`)
- SPT anchor
- negative controls
- baseline-upgrade (1p vs 1p)

Rezultat:

- `PASS` reconfirmat
- direct: `delta_chi2=-8.867375e+05`, `delta_AIC=-8.867335e+05`, `delta_BIC=-8.867209e+05`
- baseline-upgrade: `delta_chi2_memory_vs_flex=-4.439109e+05` (pass)

## 3) Fisiere actualizate

- `05_validation/evidence/qng-metric-hardening-v3.md`
- `05_validation/pre-registrations/qng-metric-hardening-v3-ds003-run-record.md`
- `05_validation/pre-registrations/qng-metric-hardening-v3-ds006-run-record.md`
- `05_validation/run-manifests/qng-t-metric-003-ds003.json`
- `05_validation/run-manifests/qng-t-metric-003-ds006.json`
- `05_validation/results-log.md`
- `05_validation/evidence/qng-t-028-trajectory.md`
- `05_validation/evidence/qng-t-039-lensing_dark.md`
- `07_exports/test-results-snapshot-2026-02-21.md`
- `TASKS.md`

## 4) Status final batch

- `Metric closure`: stabilizat (`v3` pass pe 3 datasets)
- `Trajectory main`: pass reconfirmat
- `Lensing main`: pass reconfirmat, inclusiv defensibility check

