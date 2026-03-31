# QM G19 Candidate-v4 Report

- generated_utc: `2026-03-05T23:26:40.209081Z`
- source_summary_csv: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage1-official-v13/primary_ds002_003_006_s3401_3600/summary.csv`
- profiles: `600`

## Pass Counts

- G19 v1 -> v2: `600/600 -> 600/600`
- QM lane v1 -> v2: `600/600 -> 600/600`
- improved_g19: `0`
- degraded_g19: `0`
- improved_qm_lane: `0`
- degraded_qm_lane: `0`

## Notes

- G19-v1 pass cases are preserved unchanged.
- Recovery path targets G19d only and keeps the same parsed threshold from metric checks.
- High-signal slopes are aggregated by median across fixed quantile windows.
- Multi-peak fallback uses local-window best slope over fixed r-window fractions.
- No threshold/formula edits in core gate scripts.
