# Stage-3 G11/G12 Candidate-v3 Promotion Decision

Date: 2026-03-02  
Protocol: `gr-stage3-g11-g12-candidate-v3`

## Decision

`PROMOTION-READY` as candidate policy package (official switch remains separate governance step).

## Criteria Check

- primary: `PASS`
  - `stage3: 592/600 -> 597/600`
  - improved `5`, degraded `0`
- attack A (seed500): `PASS`
  - `stage3: 1433/1500 -> 1452/1500`
  - improved `19`, degraded `0`
- holdout B: `PASS`
  - `stage3: 398/400 -> 398/400`
  - improved `0`, degraded `0`
- per-dataset non-degradation: satisfied
- degraded strict condition (`degraded=0`): satisfied in all blocks

## Remaining Primary Fails After Candidate-v3

- `3/600` remain:
  - `DS-002 seed 3436`
  - `DS-003 seed 3491`
  - `DS-006 seed 3436`

All remaining primary fails are `G11` cases.
