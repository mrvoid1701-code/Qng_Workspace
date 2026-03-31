# GR Stage-3 G11 Candidate Eval (v5)

- generated_utc: `2026-03-04T09:12:39.518702Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/summary.csv`
- profiles: `1500`

## Pass Counts (base -> candidate-v5)

- G11: `1450/1500 -> 1481/1500`
- STAGE3: `1433/1500 -> 1459/1500`
- improved_vs_base: `26`
- degraded_vs_base: `0`

## Candidate Notes

- G11a-v5 adds basin-local rank fallback for multi-peak/sparse regimes.
- G11b-v5 adds robust Theil-Sen slope fallback with unchanged threshold.
- G12 is unchanged in this candidate lane.
- No gate threshold/formula edits in official scripts.
