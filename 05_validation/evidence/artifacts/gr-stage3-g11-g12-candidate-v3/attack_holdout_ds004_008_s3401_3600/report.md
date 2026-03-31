# GR Stage-3 G11/G12 Candidate Eval (v3)

- generated_utc: `2026-03-02T13:12:49.587132Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1/summary.csv`
- profiles: `400`

## Pass Counts (official-v2 -> candidate-v3)

- G11: `398/400 -> 398/400`
- G12: `400/400 -> 400/400`
- STAGE3: `398/400 -> 398/400`
- improved_vs_v2: `0`
- degraded_vs_v2: `0`

## Candidate Notes

- Candidate-only evaluation; official policy unchanged in this script.
- G11 uses q80 OR q75 high-signal support with unchanged corr threshold (0.20).
- G12 uses winsorized slope OR plain slope with unchanged threshold (< -0.03).
- No gate threshold/formula edits in official scripts.
