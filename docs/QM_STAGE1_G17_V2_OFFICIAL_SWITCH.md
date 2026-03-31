# QM Stage-1 Official Switch (G17-v2 policy)

Date: 2026-03-02  
Effective tag: `qm-stage1-g17-v2-official`

## Why This Switch Exists

G17-v2 candidate closed prereg promotion checks with:

1. primary uplift and zero degradation,
2. attack uplift and zero degradation,
3. holdout non-degradation and uplift.

Decision evidence:

- `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.md`
- `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.md`
- `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.md`

## Frozen Official Policy (v2)

Official QM Stage-1 mapping is now:

1. `G17` official uses `G17-v2` candidate decision status.
2. `G18/G19/G20` statuses remain inherited from frozen source runs.
3. `G17-v1` is retained as legacy diagnostic status in official summaries.

No gate formulas or thresholds were changed.

## Governance Application Results

Primary (`DS-002/003/006`, seeds `3401..3600`, `n=600`):

- `G17`: `439/600 -> 564/600`
- `QM lane`: `411/600 -> 513/600`
- `degraded_vs_v1 = 0`

Attack (`DS-002/003/006`, seeds `3601..4100`, `n=1500`):

- `G17`: `1092/1500 -> 1416/1500`
- `QM lane`: `1017/1500 -> 1255/1500`
- `degraded_vs_v1 = 0`

Holdout (`DS-004/008`, seeds `3401..3600`, `n=400`):

- `G17`: `356/400 -> 400/400`
- `QM lane`: `322/400 -> 360/400`
- `degraded_vs_v1 = 0`

Official governance packages:

- `05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600/`

## Coupling Stability Check

Post-switch smoke check (`G20 + GR guard`) remains stable:

- `05_validation/evidence/artifacts/qm-gr-coupling-audit-post-g17v2-smoke-v1/report.md`
- `G20 = 3/3`
- `GR guard pre = PASS`
- `GR guard post = PASS`

## Interpretation Guardrail

- `G17-v1` global gap is treated as valid in single-peak/single-well regimes.
- `G17-v2` preserves that regime behavior and applies local-gap recovery only under multi-peak mixing.
- This is not threshold tuning; it is an observable-definition hardening for the same mass-gap/quantization-stability intent.

## Implementation

Official policy application runner:

- `scripts/tools/run_qm_stage1_official_v2.py`

Outputs:

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`
