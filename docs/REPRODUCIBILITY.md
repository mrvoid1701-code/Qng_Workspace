# REPRODUCIBILITY

Exact commands for reproducible GR-chain reruns (housekeeping only, no math edits).

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
