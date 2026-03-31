# GR Stage-3 G11/G12 Candidate Eval (v3)

- generated_utc: `2026-03-02T13:13:22.167568Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/summary.csv`
- profiles: `1500`

## Pass Counts (official-v2 -> candidate-v3)

- G11: `1450/1500 -> 1467/1500`
- G12: `1475/1500 -> 1481/1500`
- STAGE3: `1433/1500 -> 1452/1500`
- improved_vs_v2: `19`
- degraded_vs_v2: `0`

## Candidate Notes

- Candidate-only evaluation; official policy unchanged in this script.
- G11 uses q80 OR q75 high-signal support with unchanged corr threshold (0.20).
- G12 uses winsorized slope OR plain slope with unchanged threshold (< -0.03).
- No gate threshold/formula edits in official scripts.
