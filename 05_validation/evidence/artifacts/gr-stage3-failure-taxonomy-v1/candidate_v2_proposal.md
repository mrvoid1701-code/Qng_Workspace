# Stage-3 Candidate-v2 Proposal (Post-Taxonomy)

Source taxonomy:

- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/report.md`
- fail scope: `30` profiles (`G11=15`, `G12=11`, `G11+G12=4`)

## Why Candidate-v2

Dominant classes indicate two separate fragile estimators:

1. `G11` weak-correlation classes (`weak_corr_*`) including multi-peak/sparse regimes.
2. `G12d` slope-instability classes (`slope_instability_*`) with bin-support sensitivity.

`G7/G8/G9` remained stable (`600/600`) on primary Stage-3 run.

## Candidate Direction (No Threshold Changes)

- `G11a-v2`: robust high-signal rank estimator (trim-aware), candidate-only.
- `G12d-v2`: robust radial-slope estimator over supported bins, candidate-only.

Thresholds remain frozen (`corr=0.20`, `slope<-0.03`).

## Governance Rule

Promotion requires prereg closure on:

- primary (`DS-002/003/006`, `3401..3600`)
- attack A (`DS-002/003/006`, `3601..4100`)
- holdout (`DS-004/008`, `3401..3600`)

with `degraded_vs_v1=0` mandatory in every block.

Full prereg definition:

- `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v2.md`

