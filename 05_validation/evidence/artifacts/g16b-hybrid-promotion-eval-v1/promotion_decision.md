# G16b Hybrid Promotion Decision (v1)

Date: 2026-03-01

Protocol reference:

- `docs/G16B_HYBRID_PROMOTION_PREREG.md`

Evaluator:

- `scripts/tools/evaluate_g16b_hybrid_promotion_v1.py`

## Final Outcome

- Primary grid decision: `PASS`
- Attack seed-range decision: `PASS`
- Attack holdout decision: `PASS`
- Final decision: `PROMOTION-READY` (criteria satisfied across prereg + attack tests)

Official gate switch is still a separate explicit action. This report confirms the prereg evidence package is complete and passing.

## Primary Grid (DS-002/003/006, seeds 3401..3600)

Source:

- `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`

Key metrics:

- `n=600`
- `v1_pass=473`, `hybrid_pass=516`
- `improved=43`, `degraded=0`
- uplift: `+7.1667 pp`

## Attack Test A: New Seed Range (DS-002/003/006, seeds 3601..4100)

Source:

- `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`

Key metrics:

- `n=1500`
- `v1_pass=1156`, `hybrid_pass=1266`
- `improved=110`, `degraded=0`
- uplift: `+7.3333 pp`

## Attack Test B: Holdout Datasets (DS-004/008, seeds 3401..3600)

Source:

- `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

Key metrics:

- `n=400`
- `v1_pass=314`, `hybrid_pass=326`
- `improved=12`, `degraded=0`
- uplift: `+3.0000 pp`

## Notes

- Holdout datasets `DS-004` and `DS-008` currently use the default graph branch in `run_qng_action_v1.py`.
- This is still a valid anti-post-hoc check (frozen protocol, unchanged definitions), but not as strong as a domain-specific holdout generator.
