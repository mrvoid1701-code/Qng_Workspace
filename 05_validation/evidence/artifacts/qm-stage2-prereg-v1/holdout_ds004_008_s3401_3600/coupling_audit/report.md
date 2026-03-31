# QM-GR Coupling Audit Report (v2)

- generated_utc: `2026-03-04T08:07:12.756535Z`
- out_dir: `C:/Users/tigan/Desktop/qng workspace/Qng_Workspace/05_validation/evidence/artifacts/qm-stage2-prereg-v1/holdout_ds004_008_s3401_3600/coupling_audit`
- profiles_total_expected: `400`
- profiles_completed: `400`
- profiles_missing: `0`
- chunks_executed: `16`
- g20_pass: `400/400`
- g20_rc_fail_profiles: `0`
- gr_guard_pre_all_pass: `true`
- gr_guard_post_all_pass: `true`
- chunk_decisions_all_pass: `true`

## Notes

- Each chunk runs G20 profiles plus GR guard pre/post checks.
- Summary CSV is updated atomically after each chunk.
- With `--resume`, already completed profiles in summary.csv are skipped.
