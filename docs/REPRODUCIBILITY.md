# REPRODUCIBILITY

Exact commands for reproducible GR-chain reruns (housekeeping only, no math edits).

## 0) One-command reproducibility (Makefile)

Quick commands:

```bash
make gr_official_check DS=DS-003 SEED=3520
make gr_baseline_guard
make gr_sweep_phi
make gr_stage2_smoke
make gr_stage2_prereg
make gr_stage3_smoke
make gr_stage3_prereg
make gr_stage3_taxonomy
make gr_stage3_eval
make qm_lane_check DS=DS-002 SEED=3401
```

Python fallback (if `make` is unavailable):

```bash
python scripts/tools/gr_one_command.py official-check --dataset-id DS-003 --seed 3520
python scripts/tools/gr_one_command.py baseline-guard
python scripts/tools/gr_one_command.py sweep-phi
python scripts/tools/run_gr_stage2_prereg_v1.py --mode smoke
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
python scripts/tools/run_gr_stage3_prereg_v1.py --mode smoke
python scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
python scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1
python scripts/tools/evaluate_gr_stage3_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-prereg-eval-v1
python scripts/tools/run_qm_lane_check_v1.py --dataset-id DS-002 --seed 3401
```

## 1) Rerun G10..G16 for a fixed dataset + seed

Example values:

- `DATASET=DS-002`
- `SEED=3401`
- output root: `07_exports/repro/gr_chain_ds002_s3401`

```bash
python scripts/run_qng_covariant_metric_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g10
python scripts/run_qng_einstein_eq_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g11
python scripts/run_qng_gr_solutions_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g12
python scripts/run_qng_covariant_wave_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g13
python scripts/run_qng_covariant_cons_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g14
python scripts/run_qng_ppn_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g15
python scripts/run_qng_action_v1.py --dataset-id DS-002 --seed 3401 --out-dir 07_exports/repro/gr_chain_ds002_s3401/g16
```

`run_qng_action_v1.py` writes:

- `G16b` = official hybrid decision
- `G16b-v1` = legacy diagnostic
- `G16b-v2` = candidate diagnostic component

## 2) PHI scale sweep

```bash
python scripts/run_qng_phi_scale_sweep_v1.py --datasets DS-002,DS-003,DS-006 --seeds 3401 --phi-scales 0.04,0.06,0.08,0.10,0.12 --out-dir 05_validation/evidence/artifacts/phi_scale_sweep_v1
```

Main outputs:

- `05_validation/evidence/artifacts/phi_scale_sweep_v1/summary.csv`
- `05_validation/evidence/artifacts/phi_scale_sweep_v1/run-log.txt`

## 3) Compare G15b v1 vs v2

```bash
python scripts/run_qng_ppn_debug_v1.py --datasets DS-002,DS-003,DS-006 --seeds 3401 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/qng-ppn-debug-v1
```

Main output:

- `05_validation/evidence/artifacts/qng-ppn-debug-v1/summary_v1_vs_v2.csv`

DS-003 multi-seed stability check:

```bash
python scripts/run_qng_ppn_debug_v1.py --datasets DS-003 --seeds 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/qng-ppn-debug-v1-ds003-seed-sweep
```

## 4) GR regression guard (G10..G16 freeze check)

Run against frozen official baseline (current official chain includes `G15b-v2` + `G16b-hybrid`):

```bash
python scripts/run_qng_gr_regression_guard_v1.py --out-dir 05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check
```

Or via master runner:

```bash
python scripts/run_all.py --group gr-guard
```

Main outputs:

- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/observed_summary.csv`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/regression_report.json`

Survey-mode check (includes legacy diagnostic perspective):

```bash
python scripts/run_qng_gr_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json --out-dir 05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check_survey
```

## 5) Rebuild baseline JSONs from grid20 summary

Source files for the current deep baseline are tracked here:

- `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`
- `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/run-log-grid20.txt`

Rebuild survey baseline (keeps full profile grid, including expected fails in diagnostic mode):

```bash
python scripts/tools/build_gr_baseline_from_sweep.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-json 05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json --mode survey --baseline-id gr-g10-g16-regression-survey-grid20-v1 --effective-tag gr-g16b-hybrid-official --effective-commit 077478d --effective-date-utc 2026-03-02
```

Rebuild official baseline (filtered to profiles with `all_pass_official=pass`):

```bash
python scripts/tools/build_gr_baseline_from_sweep.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-json 05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json --mode official --baseline-id gr-g10-g16-regression-official-v1 --effective-tag gr-g16b-hybrid-official --effective-commit 077478d --effective-date-utc 2026-03-02
```

## 6) GR stability diagnostics from grid20 summary

```bash
python scripts/tools/analyze_gr_stability_v1.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stability-v1 --top-k 10 --tag gr-ppn-g15b-v2-official
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stability-v1/dataset_stats.csv`
- `05_validation/evidence/artifacts/gr-stability-v1/worst_cases.csv`
- `05_validation/evidence/artifacts/gr-stability-v1/report.md`

## 7) G16 failure taxonomy (diagnostics only, no threshold tuning)

```bash
python scripts/tools/run_g16_failure_taxonomy_v1.py --summary-csv 05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv --out-dir 05_validation/evidence/artifacts/g16-failure-taxonomy-v1 --top-patterns 5
```

Main outputs:

- `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_fail_cases.csv`
- `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_pass_cases.csv`
- `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16b_component_diagnostics.csv`
- `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_failure_taxonomy.md`

Definition-change proposal (candidate only):

- `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`

## 8) G16b-v2 candidate prereg evaluation (frozen protocol)

Sanity check (3 profiles):

```bash
python scripts/tools/run_g16b_v2_candidate_eval_v1.py --mode sanity
```

Full prereg run (600 profiles, fixed protocol):

```bash
python scripts/tools/run_g16b_v2_candidate_eval_v1.py --mode prereg --strict-prereg
```

Main outputs:

- `05_validation/evidence/artifacts/g16b-v2-candidate-sanity-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/report.md`
- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/prereg_manifest.json`

## 9) G16b split protocol candidate (low/high signal, frozen)

Sanity check:

```bash
python scripts/tools/run_g16b_split_protocol_v1.py --mode sanity
```

Full prereg run:

```bash
python scripts/tools/run_g16b_split_protocol_v1.py --mode prereg --strict-prereg
```

Main outputs:

- `05_validation/evidence/artifacts/g16b-split-protocol-sanity-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/report.md`
- `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/prereg_manifest.json`

## 10) G16b hybrid split evaluation (low=v2, high=v1)

Sanity check:

```bash
python scripts/tools/run_g16b_split_hybrid_v1.py --mode sanity
```

Full prereg evaluation:

```bash
python scripts/tools/run_g16b_split_hybrid_v1.py --mode prereg
```

Main outputs:

- `05_validation/evidence/artifacts/g16b-split-hybrid-sanity-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/report.md`
- `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/prereg_manifest.json`

## 11) G16b hybrid promotion prereg + attack tests

Primary promotion evaluation (DS-002/003/006, seeds 3401..3600):

```bash
python scripts/tools/evaluate_g16b_hybrid_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id g16b-hybrid-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --min-global-uplift-pp 2.0
```

Attack A: new seed range (500 seeds/dataset, frozen rules):

```bash
python scripts/tools/run_g16b_v2_candidate_eval_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3601 --seed-end 4100 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/g16b-v2-candidate-attack-seed500-v1
python scripts/tools/run_g16b_split_hybrid_v1.py --mode prereg --source-summary-csv 05_validation/evidence/artifacts/g16b-v2-candidate-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/g16b-split-hybrid-attack-seed500-v1
python scripts/tools/evaluate_g16b_hybrid_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/g16b-split-hybrid-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id g16b-hybrid-attack-seed500-v1 --strict-datasets DS-002,DS-003,DS-006 --min-global-uplift-pp 2.0
```

Attack B: holdout datasets (DS-004/008, frozen rules):

```bash
python scripts/tools/run_g16b_v2_candidate_eval_v1.py --mode prereg --datasets DS-004,DS-008 --seed-start 3401 --seed-end 3600 --phi-scale 0.08 --out-dir 05_validation/evidence/artifacts/g16b-v2-candidate-attack-holdout-v1
python scripts/tools/run_g16b_split_hybrid_v1.py --mode prereg --source-summary-csv 05_validation/evidence/artifacts/g16b-v2-candidate-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/g16b-split-hybrid-attack-holdout-v1
python scripts/tools/evaluate_g16b_hybrid_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/g16b-split-hybrid-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id g16b-hybrid-attack-holdout-v1 --strict-datasets DS-004,DS-008 --min-global-uplift-pp 2.0
```

Decision summary:

- `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/promotion_decision.md`

## 12) GR Stage-2 prereg lane (strong-field + 3+1 + tensor)

Protocol:

- `docs/GR_STAGE2_PREREG.md`

Runner:

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode smoke
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stage2-smoke-v1/summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv`

## 13) QM lane standalone checks (separate from GR decisions)

Policy:

- `docs/QM_LANE_POLICY.md`

Runner:

```bash
python scripts/tools/run_qm_lane_check_v1.py --dataset-id DS-002 --seed 3401
```

Main output:

- `07_exports/repro/qm_lane_check/<dataset_seed_tag>/summary.csv`

## 14) GR Stage-2 failure taxonomy (G11/G12)

```bash
python scripts/tools/analyze_gr_stage2_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/g11_fail_cases.csv`
- `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/g12_fail_cases.csv`
- `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-failure-taxonomy-v1/report.md`

Candidate prereg plan:

- `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v1.md`

## 15) GR Stage-2 G11/G12 candidate eval + promotion checks

Primary candidate eval:

```bash
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v1 --strict-datasets DS-002,DS-003,DS-006
```

Attack A (seed block):

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3601 --seed-end 4100 --out-dir 05_validation/evidence/artifacts/gr-stage2-attack-seed500-v1
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage2-g11-g12-attack-seed500-v1 --strict-datasets DS-002,DS-003,DS-006
```

Attack B (holdout datasets):

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-004,DS-008 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/gr-stage2-attack-holdout-v1
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v1.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v1/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage2-g11-g12-attack-holdout-v1 --strict-datasets DS-004,DS-008
```

Decision summary:

- `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v1/promotion_decision.md`

## 16) GR Stage-2 G11/G12 candidate eval v2 + promotion checks

Candidate prereg (v2):

- `05_validation/pre-registrations/gr-stage2-g11-g12-candidate-v2.md`

Primary candidate eval:

```bash
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-g12-primary-v2 --strict-datasets DS-002,DS-003,DS-006
```

Attack A (seed block):

```bash
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage2-g11-g12-attack-seed500-v2 --strict-datasets DS-002,DS-003,DS-006
```

Attack B (holdout datasets):

```bash
python scripts/tools/run_gr_stage2_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_g12_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage2-g11-g12-attack-holdout-v2 --strict-datasets DS-004,DS-008
```

Decision summary:

- `05_validation/evidence/artifacts/gr-stage2-g11-g12-promotion-eval-v2/promotion_decision.md`

## 17) GR Stage-2 official policy application (G11a-v4 switch)

Apply official Stage-2 mapping on frozen official-v3 summary profiles:

```bash
python scripts/tools/run_gr_stage2_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v4 --policy-id gr-stage2-official-v4 --effective-tag gr-stage2-g11-v4-official
```

Outputs:

- `05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-official-v4/dataset_summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-official-v4/report.md`
- `05_validation/evidence/artifacts/gr-stage2-official-v4/official_manifest.json`

## 18) GR Stage-2 baseline build + regression guard

Build frozen Stage-2 baseline from official summary:

```bash
python scripts/tools/build_gr_stage2_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --baseline-id gr-stage2-official-baseline-v1 --effective-tag gr-stage2-g11-v4-official
```

Run Stage-2 guard:

```bash
python scripts/tools/run_gr_stage2_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check
```

Outputs:

- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json`
- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/observed_summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/mismatches.csv`
- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.json`

## 19) GR Stage-2 G11 fail-only taxonomy (official-v4)

Run strict taxonomy over official-v4 `G11` fails:

```bash
python scripts/tools/analyze_gr_stage2_g11_official_fails_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4
```

Outputs:

- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4/g11_fail_cases.csv`
- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4/dataset_fail_summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4/dataset_thresholds.csv`
- `05_validation/evidence/artifacts/gr-stage2-g11-failure-taxonomy-v4/report.md`

## 20) GR Stage-2 G11a-v3 candidate prereg evaluation

Prereg definition:

- `05_validation/pre-registrations/gr-stage2-g11-candidate-v3.md`

Primary:

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-v3-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 5 --min-weak-corr-drop 2
```

Attack A:

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage2-g11-v3-attack-seed500-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 1 --min-weak-corr-drop 1
```

Attack B (holdout):

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_v3_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage2-g11-v3-attack-holdout-v1 --strict-datasets DS-004,DS-008 --min-improved 1 --min-weak-corr-drop 0
```

Decision summary:

- `05_validation/evidence/artifacts/gr-stage2-g11-v3-promotion-eval-v1/promotion_decision.md`

## 21) GR Stage-2 full rerun confirmation (official-v3)

Run strict full prereg rerun (fresh execution, no reuse):

```bash
python scripts/tools/run_gr_stage2_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg --no-reuse-existing --out-dir 05_validation/evidence/artifacts/gr-stage2-prereg-rerun-v3-600-v1
```

Re-apply governance v2 then v3 on rerun package:

```bash
python scripts/tools/run_gr_stage2_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-prereg-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v2-rerun-v3-600-v1 --policy-id gr-stage2-official-v2-rerun-v3-600-v1 --effective-tag gr-stage2-g11g12-v2-official
python scripts/tools/run_gr_stage2_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v2-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1 --policy-id gr-stage2-official-v3-rerun-v3-600-v1 --effective-tag gr-stage2-g11-v3-official
```

Consistency check vs frozen official-v3 baseline:

```bash
python scripts/tools/run_gr_stage2_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/consistency_guard
```

Decision note:

- `05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/rerun_decision.md`

## 22) G11 fail-closure + G11a-v4 candidate prereg (official-v3 baseline)

Strict fail-closure taxonomy on official-v3 rerun (6 fails scope):

```bash
python scripts/tools/analyze_gr_stage2_g11_fail_closure_v3_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-fail-closure-v3-v1
```

Primary candidate eval (`DS-002/003/006`, `3401..3600`):

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_v4_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage2-g11-v4-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 2 --max-fails-after 3
```

Attack A (seed block):

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3-for-v4/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/run_gr_stage2_g11_candidate_eval_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3-for-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_gr_stage2_g11_v4_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage2-g11-v4-attack-seed500-v1 --strict-datasets DS-002,DS-003,DS-006 --min-improved 0
```

Attack B (holdout):

```bash
python scripts/tools/run_gr_stage2_g11_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-g12-candidate-eval-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3-for-v4/attack_holdout_ds004_008_s3401_3600
python scripts/tools/run_gr_stage2_g11_candidate_eval_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v3-for-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_gr_stage2_g11_v4_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage2-g11-v4-attack-holdout-v1 --strict-datasets DS-004,DS-008 --min-improved 0
```

Decision summary:

- `05_validation/pre-registrations/gr-stage2-g11-candidate-v4.md`
- `05_validation/evidence/artifacts/gr-stage2-g11-v4-promotion-eval-v1/promotion_decision.md`

## 23) Governance switch execution record (official-v4)

Apply official-v4 on frozen official-v3 rerun package:

```bash
python scripts/tools/run_gr_stage2_official_v4.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v3-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1 --policy-id gr-stage2-official-v4-rerun-v1 --effective-tag gr-stage2-g11-v4-official
```

Consistency check vs refreshed official-v4 baseline:

```bash
python scripts/tools/run_gr_stage2_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/consistency_guard
```

Key outputs:

- `05_validation/evidence/artifacts/gr-stage2-official-v4/report.md`
- `05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/report.md`
- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/latest_check/regression_report.json`
- `05_validation/evidence/artifacts/gr-stage2-official-v4-rerun-v1/consistency_guard/regression_report.json`

## 24) GR Stage-3 prereg lane (v1, extended lanes with G8/G9)

Protocol:

- `docs/GR_STAGE3_PREREG.md`
- `05_validation/pre-registrations/gr-stage3-prereg-v1.md`

Runner:

```bash
python scripts/tools/run_gr_stage3_prereg_v1.py --mode smoke
python scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stage3-smoke-v1/summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-smoke-v1/dataset_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-smoke-v1/report.md`
- `05_validation/evidence/artifacts/gr-stage3-smoke-v1/prereg_manifest.json`
- `05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv`

## 25) GR Stage-3 primary evaluation + decision note

Run evaluation over full prereg summary:

```bash
python scripts/tools/evaluate_gr_stage3_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-prereg-eval-v1
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/status_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/dataset_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/fail_patterns.csv`
- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/report.md`
- `05_validation/evidence/artifacts/gr-stage3-prereg-eval-v1/primary_ds002_003_006_s3401_3600/decision.md`

## 26) Stage-3 failure taxonomy (strict fail scope) + candidate-v2 prereg

Run strict taxonomy over Stage-3 fails:

```bash
python scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1
```

Main outputs:

- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/fail_profiles.csv`
- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/class_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/report.md`
- `05_validation/evidence/artifacts/gr-stage3-failure-taxonomy-v1/candidate_v2_proposal.md`

Candidate-v2 prereg document (historical prereg source for official switch):

- `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v2.md`

## 27) Stage-3 governance switch (official-v2)

Apply official Stage-3 mapping from frozen candidate-v2 summary:

```bash
python scripts/tools/run_gr_stage3_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v2 --policy-id gr-stage3-official-v2 --effective-tag gr-stage3-g11g12-v2-official
```

Key outputs:

- `05_validation/evidence/artifacts/gr-stage3-official-v2/summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v2/dataset_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v2/report.md`
- `05_validation/evidence/artifacts/gr-stage3-official-v2/official_manifest.json`

## 28) Stage-3 official rerun (600 profiles) on frozen grid

Run strict Stage-3 rerun and candidate-v2 mapper:

```bash
python scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1
python scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/rerun_ds002_003_006_s3401_3600
python scripts/tools/run_gr_stage3_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/rerun_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1 --policy-id gr-stage3-official-v2-rerun-v1 --effective-tag gr-stage3-g11g12-v2-official
```

Key outputs:

- `05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v2-600-v1/report.md`
- `05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/report.md`

## 29) Stage-3 baseline refresh + guard

Build baseline and run strict regression guard:

```bash
python scripts/tools/build_gr_stage3_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --baseline-id gr-stage3-official-baseline-v1 --effective-tag gr-stage3-g11g12-v2-official
python scripts/tools/run_gr_stage3_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check
```

Key outputs:

- `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json`
- `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json`

## 30) Stage-3 official fail taxonomy (strict fail scope)

Run taxonomy only on remaining official Stage-3 fails:

```bash
python scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1
```

Key outputs:

- `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/fail_profiles.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/class_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v2-failure-taxonomy-v1/report.md`

## 31) Stage-3 candidate-v3 fail-closure (official-v2 baseline)

Pre-registration:

- `05_validation/pre-registrations/gr-stage3-g11-g12-candidate-v3.md`

Prepare official-v2 attack/holdout baseline summaries:

```bash
python scripts/tools/run_gr_stage3_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1 --policy-id gr-stage3-official-v2-attack-seed500-v1 --effective-tag gr-stage3-g11g12-v2-official
python scripts/tools/run_gr_stage3_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1 --policy-id gr-stage3-official-v2-attack-holdout-v1 --effective-tag gr-stage3-g11g12-v2-official
```

Run candidate-v3 + promotion eval (`v2 -> v3`) on all blocks:

```bash
python scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600 --eval-id gr-stage3-g11-g12-primary-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

python scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-seed500-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_seed500_ds002_003_006_s3601_4100 --eval-id gr-stage3-g11-g12-attack-seed500-v3 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

python scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v2-attack-holdout-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_gr_stage3_g11_g12_promotion_v2.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_holdout_ds004_008_s3401_3600 --eval-id gr-stage3-g11-g12-attack-holdout-v3 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift
```

Consolidated outputs:

- `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/report.md`
- primary result: `592/600 -> 597/600`, `degraded=0`
