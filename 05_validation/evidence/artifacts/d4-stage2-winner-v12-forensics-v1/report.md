# D4 Winner V12 Forensics v1

Forensics-only analysis (no formula/threshold changes).

- generated_utc: `2026-03-10T06:37:17.852406+00:00`
- dataset_id: `DS-006`
- seeds analyzed: `3401,3403,3404`
- source per-seed csv: `C:\Users\tigan\Desktop\qng workspace\Qng_Workspace\05_validation\evidence\artifacts\d4-stage2-winner-v12-strict\per_seed_candidate_summary.csv`
- source eval csv: `C:\Users\tigan\Desktop\qng workspace\Qng_Workspace\05_validation\evidence\artifacts\d4-stage2-winner-v12-strict\evaluation-v1\per_seed_evaluation.csv`

## Seed Status

- seed 3401: decision=HOLD, holdout_mond_worse_pct=-25.724236, generalization_gap_pp=20.974922
- seed 3403: decision=HOLD, holdout_mond_worse_pct=-19.987522, generalization_gap_pp=33.176771
- seed 3404: decision=HOLD, holdout_mond_worse_pct=12.576971, generalization_gap_pp=12.083704

## Top Regime Pressure (winner_over_mond > 1)

- radial:outer -> mean=1.075168, max=1.365793, worse_count=2/3

## Interpretation

- If pressure concentrates in `outer` and/or `low_accel`, next candidate should target only that regime.
- Keep strict thresholds unchanged; evaluate candidate on all 5 seeds.

Artifacts:
- `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-winner-v12-forensics-v1/failure_seed_summary.csv`
- `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-winner-v12-forensics-v1/regime_summary.csv`
- `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-winner-v12-forensics-v1/holdout_top_worst_galaxies.csv`
- `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/d4-stage2-winner-v12-forensics-v1/pattern_summary.csv`
