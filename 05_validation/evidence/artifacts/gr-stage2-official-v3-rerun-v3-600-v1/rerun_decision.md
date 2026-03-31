# GR Stage-2 Official-v3 Full Rerun Decision (600 profiles)

Date: 2026-03-02

## Scope

Frozen rerun pipeline on the same prereg grid:

- datasets: `DS-002/003/006`
- seeds: `3401..3600`
- profiles: `600`
- no threshold/formula edits

## Pipeline

1. Prereg rerun:
   - `05_validation/evidence/artifacts/gr-stage2-prereg-rerun-v3-600-v1/summary.csv`
2. Governance v2 re-application on rerun:
   - `05_validation/evidence/artifacts/gr-stage2-official-v2-rerun-v3-600-v1/summary.csv`
3. Governance v3 re-application on rerun:
   - `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/summary.csv`
4. Consistency guard vs frozen official-v3 baseline:
   - `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/consistency_guard/regression_report.json`

## Observed Results

- prereg rerun Stage-2: `570/600`
- official v2 on rerun: `587/600`
- official v3 on rerun: `594/600`
- v2 -> v3 uplift: `+7`
- degraded vs v2: `0`

## Consistency Check

Frozen baseline (`gr-stage2-g11-v3-official`) vs rerun official-v3 summary:

- decision: `PASS`
- profiles_mismatch: `0`
- profiles_missing: `0`
- profiles_extra: `0`

## Decision

Rerun confirms the official-v3 Stage-2 mapping reproduces the frozen baseline exactly on a fresh full 600-profile execution chain.
