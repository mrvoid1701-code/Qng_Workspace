# RESULT: GR + QM + Stability Sprint v2

Date: 2026-03-04  
Language: EN

## 1) GR Stage-3 (G11-v5 candidate -> official-v5)

Promotion package (`degraded=0` across all blocks):

- primary: `597/600 -> 600/600` (improved `+3`)
- attack: `1433/1500 -> 1459/1500` (improved `+26`)
- holdout: `398/400 -> 400/400` (improved `+2`)

Official artifacts:

- `05_validation/evidence/artifacts/gr-stage3-official-v5/`
- `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-seed500-v1/`
- `05_validation/evidence/artifacts/gr-stage3-official-v5-attack-holdout-v1/`

Guard status:

- `gr-stage3-regression-baseline-v2/latest_check`: `PASS`

## 2) QM Stage-1 (G17-v3 candidate -> official-v4)

Promotion package (`degraded=0` across all blocks):

- primary lane: `411/600 -> 513/600` (improved `+102`)
- attack lane: `1017/1500 -> 1255/1500` (improved `+238`)
- holdout lane: `322/400 -> 360/400` (improved `+38`)

Official artifacts:

- `05_validation/evidence/artifacts/qm-stage1-official-v4/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v4/attack_holdout_ds004_008_s3401_3600/`

Guard status:

- `qm-stage1-regression-baseline-v2/latest_check`: `PASS`

Post-switch taxonomy:

- `qm-stage1-failure-taxonomy-v2/report.md`
- fail profiles: `372/2500` (`14.88%`)
- dominant failing gate: `G18`

## 3) Coupling Backbone (v2 bundle)

Frozen coupling bundle remains clean:

- `profiles_completed`: `2500/2500`
- `g20_pass`: `2500/2500`
- `gr_guard_pre/post`: `PASS`
- bundle: `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/bundle-v1/`

Duration note:

- the full `2500`-profile coupling run was a long job (`~5 hours` wall-clock on this machine).

## 4) Stability Stress Add-ons (requested pack)

Executed packs:

1. dual stability sweep  
   `05_validation/evidence/artifacts/stability-dual-sweep-v1/`
2. chi-sigma phase diagram  
   `05_validation/evidence/artifacts/stability-phase-diagram-chi-sigma-v1/`
3. scaling test (+ convergence v6 check)  
   `05_validation/evidence/artifacts/stability-scaling-test-v1/`
4. perturbation torture test  
   `05_validation/evidence/artifacts/stability-perturbation-torture-v1/`
5. long emergence run  
   `05_validation/evidence/artifacts/stability-long-emergence-v1/`

Quick readout:

- Structural channel remains stable (`S2` checks pass).
- Energy drift gate remains the dominant stress-limiter in hard regimes.
- Scaling v6 check on this mini block is `FAIL` due bulk CI crossing zero (full CI still negative).

## 5) Scope Guard

- no threshold tuning
- no core formula changes
- governance + diagnostics + evidence packaging only
