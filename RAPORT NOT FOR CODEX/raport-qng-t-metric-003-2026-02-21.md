# Raport Executie - QNG-T-METRIC-003 (2026-02-21)

## 1) Summary

Am dus `P8-METRIC` pe varianta `v3` pe directia solicitata: metrica extrasa din dinamica (`Hessian(Sigma)`), cu lock nou (`metric-lock-v3`), prereg nou si rulare completa.  
`v1` si `v2` raman pastrate ca istoric de falsificare/imbunatatire, fara retuning de gates.

## 2) Decision + Reason

**Decision: PASS** pentru `QNG-T-METRIC-003` (`QNG-CORE-METRIC-V3`).  
Motiv: toate gate-urile preregistrate `D1-D4` au trecut sub setari blocate, fara schimbarea pragurilor.

## 3) Key Metrics

| Gate | Metric | Valoare | Prag | Status |
| --- | --- | ---: | ---: | --- |
| D1 | `min_eig_global` | `0.300856` | `>= 1e-8` | pass |
| D2 | `median_delta_g` | `0.056367` | `<= 0.10` | pass |
| D2 | `p90_delta_g` | `0.178355` | `<= 0.25` | pass |
| D3 | `median_cos_sim` | `0.992374` | `>= 0.90` | pass |
| D3 | `p10_cos_sim` | `0.960620` | `>= 0.70` | pass |
| D4 | `median_cos_sim_shuffled` | `-0.133569` | `< 0.55` | pass |
| FINAL | `decision` | `pass` | `D1&D2&D3&D4` | pass |

## 4) Files Changed

- `scripts/run_qng_metric_hardening_v3.py`
- `01_notes/metric/metric-lock-v3.md`
- `05_validation/pre-registrations/qng-metric-hardening-v3.md`
- `05_validation/evidence/qng-metric-hardening-v3.md`
- `05_validation/run-manifests/qng-t-metric-003.json`
- `05_validation/test-plan.md`
- `05_validation/results-log.md`
- `05_validation/dataset-manifest.json`
- `07_exports/test-results-snapshot-2026-02-21.md`
- `TASKS.md`

## 5) New/Updated Preregs

- Nou: `05_validation/pre-registrations/qng-metric-hardening-v3.md`
- Istoric pastrat: `05_validation/pre-registrations/qng-metric-hardening-v1.md`, `05_validation/pre-registrations/qng-metric-hardening-v2.md`

## 6) Artifacts

- `05_validation/evidence/artifacts/qng-metric-hardening-v3/metric_checks.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/eigs.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/drift.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/align_sigma.csv`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/config.json`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/run-log.txt`
- `05_validation/evidence/artifacts/qng-metric-hardening-v3/artifact-hashes.json`

## 7) Credibility Tag

- `authenticity: silver`
- `leakage_risk: low`
- `negative_control: done`

## 8) Next Actions

1. Ruleaza acelasi lock `v3` pe `DS-003` si `DS-006` fara nicio schimbare.
2. Daca trece si cross-dataset, promoveaza closure metric ca stabil.
3. Revino la testele principale trajectory/lensing cu metric closure consolidat.

