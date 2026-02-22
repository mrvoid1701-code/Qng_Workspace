# Raport Executie - Bulletproof Add-ons (2026-02-21)

## Ce s-a implementat

1. **Repro Pack public (v1)**
- `07_exports/repro-pack-v1/repro-pack-v1-manifest.json`
- `07_exports/repro-pack-v1/repro-pack-v1-artifact-hashes.csv`
- `07_exports/repro-pack-v1/reproduce_all.ps1`
- `07_exports/repro-pack-v1/HOW_TO_REPRODUCE_30_MIN.md`

2. **Control anti-leak / anti-shortcut suplimentar (metric)**
- Script nou: `scripts/run_qng_metric_anti_leak_v1.py`
- Prereg nou: `05_validation/pre-registrations/qng-metric-anti-leak-v1.md`
- Evidence nou: `05_validation/evidence/qng-metric-anti-leak-v1.md`
- Manifest nou: `05_validation/run-manifests/qng-t-metric-004.json`

3. **Statement clar pentru paper**
- `06_writing/paper-valid-only.md`
- `06_writing/paper-draft.md`

## Rezultate control anti-leak (`QNG-T-METRIC-004`)

- `positive_median_cos = 0.992374`
- `label_perm_median_cos = 0.242666` (pass)
- `rewire_median_of_medians = 0.036314` (pass)
- `rewire_shuffled_median_of_medians = -0.068478` (pass)
- `overall_pass = True`

Interpretare:
- controlul nou de **graph-rewire** + varianta combinata cu label permutation au colapsat semnalul cum era asteptat.

## Bookkeeping actualizat

- `05_validation/test-plan.md` (adaugat `QNG-T-METRIC-004`)
- `05_validation/results-log.md` (run journal + status per-test)
- `05_validation/dataset-manifest.json` (test/claim mapping)
- `07_exports/test-results-snapshot-2026-02-21.md` (snapshot extins)
- `TASKS.md` (bulletproof add-ons marcate)

## Concluzie

Pachetul este acum semnificativ mai greu de atacat in review:
- reproducibilitate publica standardizata
- control suplimentar anti-shortcut pe metric
- wording de status clar in documentul de paper
- scriptul `reproduce_all.ps1` a fost rulat cap-coada cu succes si a confirmat prezenta tuturor artefactelor obligatorii
