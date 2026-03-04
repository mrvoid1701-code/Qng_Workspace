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
make qm_stage1_smoke
make qm_gr_coupling_audit_smoke
make qm_g17_diag_ds003
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

## 46) Stability energy candidate-v2 (anti post-hoc)

Frozen prereg:

- `05_validation/pre-registrations/qng-stability-energy-covariant-v2.md`

Run all three prereg blocks + promotion checks:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-PRIMARY --seed 3401 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/primary_s3401 --no-strict-exit
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-ATTACK --seed-list 3401,4401 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/attack_s3401_4401 --no-strict-exit
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-HOLDOUT --seed-list 3401 --n-nodes-list 30,42 --steps-list 80 --out-dir 05_validation/evidence/artifacts/stability-v1-prereg-v2/holdout_n30_42_s3401 --no-strict-exit

python scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/primary_s3401/summary.csv --strict-datasets STABILITY-PRIMARY --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401 --energy-threshold 0.90 --eval-id stability-energy-covariant-primary-v2
python scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/attack_s3401_4401/summary.csv --strict-datasets STABILITY-ATTACK --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401 --energy-threshold 0.90 --eval-id stability-energy-covariant-attack-v2
python scripts/tools/run_stability_energy_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-v1-prereg-v2/holdout_n30_42_s3401/summary.csv --strict-datasets STABILITY-HOLDOUT --out-dir 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401 --energy-threshold 0.90 --eval-id stability-energy-covariant-holdout-v2

python scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401/summary.csv --strict-datasets STABILITY-PRIMARY --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/primary_s3401 --eval-id stability-energy-promotion-primary-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift
python scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401/summary.csv --strict-datasets STABILITY-ATTACK --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/attack_s3401_4401 --eval-id stability-energy-promotion-attack-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift
python scripts/tools/evaluate_stability_energy_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401/summary.csv --strict-datasets STABILITY-HOLDOUT --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/holdout_n30_42_s3401 --eval-id stability-energy-promotion-holdout-v1 --require-zero-degraded --require-non-energy-stable --require-energy-uplift

python scripts/tools/summarize_stability_energy_promotion_v1.py --report-jsons 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/primary_s3401/report.json,05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/attack_s3401_4401/report.json,05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/holdout_n30_42_s3401/report.json --out-dir 05_validation/evidence/artifacts/stability-energy-promotion-eval-v1 --eval-id stability-energy-promotion-bundle-v1
```

Main outputs:

- `05_validation/evidence/artifacts/stability-energy-covariant-v2/*/summary.csv`
- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/*/report.json`
- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/promotion_decision.md`

## 47) Stability official-v2 apply + baseline guard

Apply official policy mapping (governance-layer switch):

```bash
python scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/primary_s3401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/primary_s3401 --policy-id stability-official-v2 --effective-tag stability-energy-v2-official
python scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/attack_s3401_4401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/attack_s3401_4401 --policy-id stability-official-v2-attack --effective-tag stability-energy-v2-official
python scripts/tools/run_stability_official_v2.py --source-summary-csv 05_validation/evidence/artifacts/stability-energy-covariant-v2/holdout_n30_42_s3401/summary.csv --out-dir 05_validation/evidence/artifacts/stability-official-v2/holdout_n30_42_s3401 --policy-id stability-official-v2-holdout --effective-tag stability-energy-v2-official
```

Build baselines + run guard:

```bash
python scripts/tools/build_stability_baseline_v1.py --block primary
python scripts/tools/build_stability_baseline_v1.py --block attack
python scripts/tools/build_stability_baseline_v1.py --block holdout
python scripts/tools/run_stability_regression_guard_v1.py --out-dir 05_validation/evidence/artifacts/stability-regression-baseline-v1/latest_check
```

Or via Makefile:

```bash
make stability_official_apply_primary
make stability_official_apply_attack
make stability_official_apply_holdout
make stability_baseline_build
make stability_regression_guard
```

## 48) Stability convergence gate (discrete -> continuum contract)

Frozen prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v1.md`

Run:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V1 --seed-list 3401 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v1/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v1.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v1/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v1 --step-tol 0.002 --min-step-pass-fraction 0.75 --min-overall-improvement 0.005 --support-worsen-factor-max 1.25
```

Or:

```bash
make stability_convergence_v1
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v1/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v1/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v1/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v1/report.json`

## 49) Stability convergence gate v2 (bulk/full + scaling + cross-seed)

Frozen prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v2.md`

Run (20 seeds):

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V2 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v2/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v2.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2 --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85
```

Or:

```bash
make stability_convergence_v2
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v2/report.json`

## 50) Stability convergence v2 bulk-fail taxonomy + diagnostic sweep (non-promotion)

Purpose:

- classify bulk FAIL seeds from v2 without threshold changes
- run sensitivity diagnostics for bulk mask strategy only

Locked diagnostic prereg:

- `05_validation/pre-registrations/stability-convergence-v2-diagnostic-sweep.md`

Run:

```bash
python scripts/tools/analyze_stability_convergence_v2_failures_v1.py --report-json 05_validation/evidence/artifacts/stability-convergence-v2/report.json --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v2/seed_checks.csv --level-stats-csv 05_validation/evidence/artifacts/stability-convergence-v2/level_stats.csv --step-checks-csv 05_validation/evidence/artifacts/stability-convergence-v2/step_checks.csv --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1
python scripts/tools/run_stability_convergence_v2_diagnostic_sweep_v1.py --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1 --mask-quantiles 0.00,0.25,0.50,0.75 --bulk-levels 30,36,42 --min-profiles-per-level 5
```

Or:

```bash
make stability_convergence_v2_analysis
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/bulk_fail_seeds.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/bulk_vs_full_delta.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/bulk_fail_profile_levels.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-failure-taxonomy-v1/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/bulk_rho_sweep.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/bulk_rho_heatmap.csv`
- `05_validation/evidence/artifacts/stability-convergence-v2-diagnostic-sweep-v1/report.md`

## 51) Stability convergence gate v3 (Sigma-mask core-stable bulk)

Locked prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v3.md`

Run:

```bash
python scripts/tools/run_stability_convergence_gate_v3.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v2/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v3 --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5
```

Or:

```bash
make stability_convergence_v3_gate
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v3/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v3/report.json`
- `05_validation/pre-registrations/qng-stability-convergence-v3-run-record-2026-03-03.md`

## 52) Stability convergence gate v3b (connected central component bulk metric)

Locked prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v3b.md`

Run:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V3B --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v3b/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v3.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v3b/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v3b --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v3b.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel_core_cc --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --rho-bulk-max -0.80 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --no-strict-exit
```

Or:

```bash
make stability_convergence_v3b
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v3b/raw/summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v3b/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v3b/report.json`
- `05_validation/pre-registrations/qng-stability-convergence-v3b-run-record-2026-03-03.md`

## 53) Stability convergence gate v4 (robust bulk trend estimator)

Locked prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v4.md`

Run:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V4 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,30,36,42,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v4/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v4 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v4.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit
```

Or:

```bash
make stability_convergence_v4
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v4/report.json`
- `05_validation/pre-registrations/qng-stability-convergence-v4-run-record-2026-03-03.md`

## 54) Stability convergence v4 failure taxonomy (diagnostic only)

Run:

```bash
python scripts/tools/analyze_stability_convergence_v4_failures_v1.py --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v4/seed_checks.csv --level-stats-csv 05_validation/evidence/artifacts/stability-convergence-v4/level_stats.csv --raw-summary-csv 05_validation/evidence/artifacts/stability-convergence-v4/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1
```

Or:

```bash
make stability_convergence_v4_taxonomy
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/v4_fail_seeds.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/tau_distribution.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/ci_width_audit.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/support_collapse_summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v4-failure-taxonomy-v1/report.md`

## 55) Stability convergence gate v5 (expanded levels)

Locked prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v5.md`

Run:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V5 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,28,32,36,40,44,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v5/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v5/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v5 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v5.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit
```

Or:

```bash
make stability_convergence_v5
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v5/raw/summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/step_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v5/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v5/report.json`
- `05_validation/pre-registrations/qng-stability-convergence-v5-run-record-2026-03-03.md`

## 56) Stability dual-attributes diagnostic (S1 energetic vs S2 structural)

Run:

```bash
python scripts/tools/analyze_stability_dual_attributes_v1.py --run-dirs 05_validation/evidence/artifacts/stability-convergence-v4,05_validation/evidence/artifacts/stability-convergence-v5 --out-dir 05_validation/evidence/artifacts/stability-dual-attributes-v1
```

Or:

```bash
make stability_dual_attributes
```

Main outputs:

- `05_validation/evidence/artifacts/stability-dual-attributes-v1/lane_summary.csv`
- `05_validation/evidence/artifacts/stability-dual-attributes-v1/seed_dual_attributes.csv`
- `05_validation/evidence/artifacts/stability-dual-attributes-v1/report.md`

## 57) Stability dual-channel governance + v6 candidate run

Governance doc:

- `docs/STABILITY_DUAL_CHANNELS.md`

Candidate prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v6.md`

Run:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V6 --seed-list 3401,3402,3403,3404,3405,3406,3407,3408,3409,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420 --n-nodes-list 24,28,32,36,40,44,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit
```

Or:

```bash
make stability_convergence_v6
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6/seed_checks.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6/level_stats.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6/report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6/report.json`
- `05_validation/pre-registrations/qng-stability-convergence-v6-run-record-2026-03-03.md`

## 58) Stability convergence v6 promotion audit (primary + attack + shifted holdout)

Run primary comparator packages (legacy v5-like vs v6):

```bash
python scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/legacy_v5like --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v5.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit
```

Run attack seed block:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V6-ATTACK --seed-list 3601,3602,3603,3604,3605,3606,3607,3608,3609,3610,3611,3612,3613,3614,3615,3616,3617,3618,3619,3620 --n-nodes-list 24,28,32,36,40,44,48 --steps-list 60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/legacy_v5like --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v5.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit
```

Run shifted holdout regime:

```bash
python scripts/tools/run_stability_stress_v1.py --dataset-id STABILITY-CONVERGENCE-V6-HOLDOUT --seed-list 3501,3502,3503,3504,3505,3506,3507,3508,3509,3510,3511,3512,3513,3514,3515,3516,3517,3518,3519,3520 --n-nodes-list 30,36,42,48 --steps-list 80 --edge-prob-grid 0.05,0.12,0.25 --chi-scale-grid 0.40,1.00,1.80 --noise-grid 0.00,0.02,0.05 --phi-shock-grid 0.00,0.60 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/raw --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v4.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/legacy_v5like --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v5.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --step-tol 0.002 --full-step-fraction-min 0.75 --bulk-step-fraction-min 0.85 --overall-improvement-min 0.005 --support-worsen-factor-max 1.25 --rho-full-max -0.60 --full-seed-pass-fraction-min 0.85 --bulk-seed-pass-fraction-min 0.85 --bulk-min-profiles-per-level 5 --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-bootstrap-reps 400 --bulk-ci-alpha 0.05 --no-strict-exit
python scripts/tools/run_stability_convergence_gate_v6.py --summary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/raw/summary.csv --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6.md --full-metric-field delta_energy_rel --bulk-metric-field delta_energy_rel --bulk-core-size-min 6 --bulk-core-ratio-min 0.10 --bulk-min-profiles-per-level 5 --bootstrap-reps 2000 --ci-alpha 0.05 --no-strict-exit
```

Aggregate promotion audit:

```bash
python scripts/tools/evaluate_stability_convergence_v6_promotion_v1.py --audit-root 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1 --blocks primary_s3401_3420,attack_seed3601_3620,holdout_regime_shift_s3501_3520 --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1 --eval-id stability-convergence-v6-promotion-eval-v1
```

Or:

```bash
make stability_convergence_v6_promotion_eval
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/block_summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/promotion_report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/promotion_report.json`

## 59) Stability convergence v6 baseline + regression guard + telemetry

Build frozen baselines (primary/attack/holdout):

```bash
python scripts/tools/build_stability_convergence_v6_baseline_v1.py --block primary --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json --baseline-id stability-convergence-v6-baseline-primary-v1 --effective-tag stability-convergence-v6-official
python scripts/tools/build_stability_convergence_v6_baseline_v1.py --block attack --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json --baseline-id stability-convergence-v6-baseline-attack-v1 --effective-tag stability-convergence-v6-official
python scripts/tools/build_stability_convergence_v6_baseline_v1.py --block holdout --seed-checks-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/seed_checks.csv --report-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/report.json --out-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json --baseline-id stability-convergence-v6-baseline-holdout-v1 --effective-tag stability-convergence-v6-official
```

Run regression guard (non-degradation + profile-set checks + pass-stays-pass):

```bash
python scripts/tools/run_stability_convergence_v6_regression_guard_v1.py --baseline-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json --baseline-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json --baseline-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json --seed-checks-primary-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/seed_checks.csv --seed-checks-attack-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/seed_checks.csv --seed-checks-holdout-csv 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/seed_checks.csv --report-primary-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/primary_s3401_3420/v6_candidate/report.json --report-attack-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/attack_seed3601_3620/v6_candidate/report.json --report-holdout-json 05_validation/evidence/artifacts/stability-convergence-v6-audit-v1/holdout_regime_shift_s3501_3520/v6_candidate/report.json --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check
```

Or:

```bash
make stability_convergence_v6_baseline_build
make stability_convergence_v6_regression_guard
make stability_convergence_v6_telemetry
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_primary.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_attack.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/stability_convergence_v6_baseline_holdout.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check/regression_report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check/regression_report.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-regression-baseline-v1/latest_check/telemetry.csv`

## 60) Stability convergence v6 extended audit (200 seeds/block)

Locked prereg:

- `05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1.md`

Run (resumable orchestrator):

```bash
python scripts/tools/run_stability_convergence_v6_extended_eval_v1.py --out-dir 05_validation/evidence/artifacts/stability-convergence-v6-extended-v1 --prereg-doc 05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1.md --resume
```

Or:

```bash
make stability_convergence_v6_extended_eval
```

Main outputs:

- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/block_summary.csv`
- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/promotion_report.md`
- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/promotion_report.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/manifest.json`
- `05_validation/evidence/artifacts/stability-convergence-v6-extended-v1/run-log.txt`
- `05_validation/pre-registrations/qng-stability-convergence-v6-extended-v1-run-record-2026-03-03.md`

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

## 32) Stage-3 official-v3 confirmation (rerun + guard + strict fail taxonomy)

Run the frozen rerun and apply official-v3 mapping:

```bash
python scripts/tools/run_gr_stage3_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v3-600-v1
python scripts/tools/run_gr_stage3_g11_g12_candidate_eval_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-prereg-rerun-v3-600-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/rerun_ds002_003_006_s3401_3600
python scripts/tools/run_gr_stage3_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/rerun_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1 --policy-id gr-stage3-official-v3-rerun-v1 --effective-tag gr-stage3-g11g12-v3-official
```

Run baseline build + guard + strict fail taxonomy:

```bash
python scripts/tools/build_gr_stage3_baseline_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --baseline-id gr-stage3-official-baseline-v1 --effective-tag gr-stage3-g11g12-v3-official
python scripts/tools/run_gr_stage3_regression_guard_v1.py --baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check
python scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-failure-taxonomy-v1
```

Expected readout:

- official-v3 rerun: `Stage-3 570/600 -> 597/600`, `degraded_vs_v2=0`
- guard decision: `PASS` (`profiles_missing=0`, `profiles_mismatch=0`)
- strict fail scope: `3` (`G11` only)

## 33) QM-Stage-1 prereg + evaluation + QM-GR coupling audit

Pre-registration:

- `05_validation/pre-registrations/qm-stage1-prereg-v1.md`

Smoke package:

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-stage1-smoke-v1
python scripts/tools/evaluate_qm_stage1_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/qm-stage1-smoke-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-eval-v1/smoke_ds002_003_006_s3401 --eval-id qm-stage1-smoke-v1 --strict-datasets DS-002,DS-003,DS-006 --require-zero-rc --min-all-pass-rate 0.0
```

Frozen primary prereg package:

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-002,DS-003,DS-006 --seed-start 3401 --seed-end 3600 --strict-prereg --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-v1
python scripts/tools/evaluate_qm_stage1_prereg_v1.py --summary-csv 05_validation/evidence/artifacts/qm-stage1-prereg-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-stage1-primary-v1 --strict-datasets DS-002,DS-003,DS-006 --require-zero-rc --min-all-pass-rate 0.0
```

QM-GR coupling audit (G20 + Stage-3 GR guard stability):

```bash
python scripts/tools/run_qm_gr_coupling_audit_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-smoke-v1 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv
```

## 34) G17 DS-003 mini-sprint diagnosis (seeds 3401..3430)

Run targeted diagnosis batch:

```bash
python scripts/tools/run_g17_diagnosis_v1.py --dataset-id DS-003 --seed-start 3401 --seed-end 3430 --out-dir 05_validation/evidence/artifacts/g17-diagnosis-ds003-v1
```

Key outputs:

- `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/summary.csv`
- `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/class_summary.csv`
- `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/g17-diagnosis-ds003-v1/report.md`

## 35) QM G17 candidate-v2 (hybrid local-gap) DS-003 mini + promotion eval

Build DS-003 mini source package (`3401..3430`):

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-003 --seed-start 3401 --seed-end 3430 --out-dir 05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1
```

Run candidate-v2 hybrid policy on frozen summary:

```bash
python scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430
```

Run promotion evaluator with strict non-degradation checks:

```bash
python scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/ds003_s3401_3430 --eval-id qm-g17-ds003-mini-v2 --strict-datasets DS-003 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift
```

Key outputs:

- `05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1/summary.csv`
- `05_validation/evidence/artifacts/qm-stage1-ds003-mini-v1/dataset_summary.csv`
- `05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430/summary.csv`
- `05_validation/evidence/artifacts/qm-g17-candidate-v2/ds003_s3401_3430/report.md`
- `05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/ds003_s3401_3430/report.md`

## 36) QM G17 candidate-v2 full prereg blocks (primary + attack + holdout)

Run Stage-1 source packages:

```bash
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-002 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds002_s3401_3600
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-003 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds003_s3401_3600
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-006 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds006_s3401_3600

python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-002 --seed-start 3601 --seed-end 4100 --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds002_s3601_4100
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-003 --seed-start 3601 --seed-end 4100 --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds003_s3601_4100
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-006 --seed-start 3601 --seed-end 4100 --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds006_s3601_4100

python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-004 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/ds004_s3401_3600
python scripts/tools/run_qm_stage1_prereg_v1.py --mode prereg --datasets DS-008 --seed-start 3401 --seed-end 3600 --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/ds008_s3401_3600
```

Combine Stage-1 summaries:

```bash
python scripts/tools/combine_qm_stage1_summaries_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds002_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds003_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/ds006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/combined_ds002_003_006_s3401_3600
python scripts/tools/combine_qm_stage1_summaries_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds002_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds003_s3601_4100/summary.csv,05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/ds006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/combined_ds002_003_006_s3601_4100
python scripts/tools/combine_qm_stage1_summaries_v1.py --summary-csvs 05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/ds004_s3401_3600/summary.csv,05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/ds008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/combined_ds004_008_s3401_3600
```

Run candidate-v2 and promotion eval:

```bash
python scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-prereg-primary-v1/combined_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600
python scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/primary_ds002_003_006_s3401_3600 --eval-id qm-g17-primary-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --require-net-uplift

python scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-attack-seed500-v1/combined_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_seed500_ds002_003_006_s3601_4100
python scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100 --eval-id qm-g17-attack-seed500-v2 --strict-datasets DS-002,DS-003,DS-006 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift

python scripts/tools/run_qm_g17_candidate_eval_v2.py --source-summary-csv 05_validation/evidence/artifacts/qm-stage1-attack-holdout-v1/combined_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_holdout_ds004_008_s3401_3600
python scripts/tools/evaluate_qm_g17_promotion_v1.py --summary-csv 05_validation/evidence/artifacts/qm-g17-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-g17-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600 --eval-id qm-g17-attack-holdout-v2 --strict-datasets DS-004,DS-008 --require-zero-degraded --require-per-dataset-nondegrade --no-require-net-uplift
```

Run post-candidate QM-GR coupling smoke:

```bash
python scripts/tools/run_qm_gr_coupling_audit_v1.py --mode smoke --datasets DS-002,DS-003,DS-006 --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-post-g17v2-smoke-v1 --gr-baseline-json 05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/gr_stage3_baseline_official.json --gr-summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv
```

## 37) QM Stage-1 official switch apply (G18d-v2 governance)

Apply official policy packages from frozen `G18` candidate-v2 summaries:

```bash
python scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/primary_ds002_003_006_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/primary_ds002_003_006_s3401_3600 --policy-id qm-stage1-official-v3 --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2
python scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_seed500_ds002_003_006_s3601_4100/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_seed500_ds002_003_006_s3601_4100 --policy-id qm-stage1-official-v3-attack-seed500 --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2
python scripts/tools/run_qm_stage1_official_v3.py --source-summary-csv 05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --reference-summary-csv 05_validation/evidence/artifacts/qm-stage1-official-v2/attack_holdout_ds004_008_s3401_3600/summary.csv --out-dir 05_validation/evidence/artifacts/qm-stage1-official-v3/attack_holdout_ds004_008_s3401_3600 --policy-id qm-stage1-official-v3-attack-holdout --effective-tag qm-stage1-g18-v2-official --source-policy-id qm-g18-candidate-v2-hybrid-local-ds --reference-policy-id qm-stage1-official-v2
```

Equivalent one-command targets:

```bash
make qm_stage1_official_apply_primary
make qm_stage1_official_apply_attack
make qm_stage1_official_apply_holdout
```

Key outputs (per block):

- `summary.csv`
- `dataset_summary.csv`
- `report.md`
- `official_manifest.json`

## 38) QM Stage-1 baseline build + regression guard

Build baselines (primary + attack + holdout):

```bash
make qm_stage1_baseline_build
```

Run guard:

```bash
make qm_stage1_regression_guard
```

Outputs:

- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_primary.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_attack.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/qm_stage1_baseline_holdout.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/regression_report.json`
- `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/regression_report.md`

## 39) QM Stage-1 failure taxonomy (post-switch)

Run taxonomy from existing official-v3 summaries:

```bash
make qm_stage1_taxonomy
```

Outputs:

- `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/qm_fail_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/qm_pass_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/pattern_summary.csv`
- `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/feature_correlations.csv`
- `05_validation/evidence/artifacts/qm-stage1-failure-taxonomy-v2/report.md`

## 40) QM Stage-1 G18 failure taxonomy (strict subgate focus)

Run strict G18 taxonomy:

```bash
make qm_stage1_g18_taxonomy
```

Outputs:

- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/g18_fail_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/g18_pass_cases.csv`
- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/pattern_summary_g18_subgates.csv`
- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/regime_summary.csv`
- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/feature_correlations.csv`
- `05_validation/evidence/artifacts/qm-stage1-g18-failure-taxonomy-v2/report.md`

## 41) QM G18d candidate-v2 prereg blocks + promotion eval

Run candidate blocks:

```bash
make qm_g18_candidate_v2_primary
make qm_g18_candidate_v2_attack
make qm_g18_candidate_v2_holdout
```

Run promotion eval:

```bash
make qm_g18_promotion_primary
make qm_g18_promotion_attack
make qm_g18_promotion_holdout
```

Outputs:

- `05_validation/evidence/artifacts/qm-g18-candidate-v2/primary_ds002_003_006_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_seed500_ds002_003_006_s3601_4100/`
- `05_validation/evidence/artifacts/qm-g18-candidate-v2/attack_holdout_ds004_008_s3401_3600/`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/primary_ds002_003_006_s3401_3600/report.json`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/report.json`
- `05_validation/evidence/artifacts/qm-g18-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/report.json`

## 42) QM-GR coupling audit v2 (chunked + resumable)

Chunked commands (resume-safe, low-artifact mode):

```bash
make qm_gr_coupling_audit_primary_chunked
make qm_gr_coupling_audit_attack_chunked
make qm_gr_coupling_audit_holdout_chunked
```

Direct runner example:

```bash
python scripts/tools/run_qm_gr_coupling_audit_v2.py --ds-list DS-002,DS-003,DS-006 --seed-min 3401 --seed-max 3600 --chunk-size 25 --resume --out-dir 05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/primary_ds002_003_006_s3401_3600 --no-write-artifacts --no-plots
```

Resume behavior:

- reads existing `summary.csv`
- skips completed `(dataset_id, seed)` profiles when `--resume` is set
- writes `summary.csv` atomically after each chunk

Outputs per package:

- `summary.csv`
- `dataset_summary.csv`
- `chunk_checks.csv`
- `report.md`
- `manifest.json`
- `run-log.txt`

## 43) QM Stage-1 freeze verification (official-v3 + guard + smoke)

Run official guard:

```bash
make qm_stage1_regression_guard
```

Run fast smoke:

```bash
python scripts/tools/run_qm_lane_check_v1.py --dataset-id DS-003 --seed 3520 --out-dir 07_exports/repro/qm_stage1_freeze_smoke_ds003_s3520
```

Expected:

- regression guard decision `PASS` in:
  - `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v1/latest_check/regression_report.json`
- smoke `all_pass_qm_lane=pass` in:
  - `07_exports/repro/qm_stage1_freeze_smoke_ds003_s3520/summary.csv`

## 44) Stability term strict sweep (QNG-v1-strict)

Policy/derivations:

- `docs/STABILITY_V1_STRICT.md`
- `03_math/derivations/qng-stability-action-v1.md`
- `03_math/derivations/qng-stability-update-v1.md`
- `05_validation/pre-registrations/qng-stability-v1-strict.md`

Run:

```bash
make stability_v1_stress
```

Direct Python fallback:

```bash
python scripts/tools/run_stability_stress_v1.py --out-dir 05_validation/evidence/artifacts/stability-v1
```

Outputs:

- `05_validation/evidence/artifacts/stability-v1/summary.csv`
- `05_validation/evidence/artifacts/stability-v1/gate_summary.csv`
- `05_validation/evidence/artifacts/stability-v1/report.md`
- `05_validation/evidence/artifacts/stability-v1/manifest.json`
- `05_validation/evidence/artifacts/stability-v1/run-log.txt`

## 45) Stability fail taxonomy (v1 strict)

Run taxonomy on strict sweep summary:

```bash
make stability_v1_taxonomy
```

Direct Python fallback:

```bash
python scripts/tools/analyze_stability_v1_failures_v1.py --summary-csv 05_validation/evidence/artifacts/stability-v1/summary.csv --out-dir 05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1
```

Outputs:

- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/fail_cases.csv`
- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/pass_cases.csv`
- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/report.md`

## 46) QM Stage-2 prereg orchestration (candidate lane)

Protocol:

- `docs/QM_STAGE2_PREREG.md`

Smoke run:

```bash
make qm_stage2_smoke
```

Full prereg orchestration:

```bash
make qm_stage2_prereg
```

Direct runner:

```bash
python scripts/tools/run_qm_stage2_prereg_v1.py --mode smoke --execute --with-coupling-audit --chunk-size 25 --resume-coupling --no-write-artifacts --no-plots
python scripts/tools/run_qm_stage2_prereg_v1.py --mode prereg --strict-prereg --execute --with-coupling-audit --resume-qm-lane --chunk-size 25 --resume-coupling --no-write-artifacts --no-plots
```

Outputs:

- `05_validation/evidence/artifacts/qm-stage2-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/qm-stage2-prereg-v1/report.md`
- `05_validation/evidence/artifacts/qm-stage2-prereg-v1/manifest.json`
- per-block outputs under:
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/<block_id>/qm_lane/`
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/<block_id>/eval/`
  - `05_validation/evidence/artifacts/qm-stage2-prereg-v1/<block_id>/coupling_audit/`

## 47) GR Stage-3 strict fail-closure diagnostics (official-v3 rerun source)

Run strict taxonomy on the official Stage-3 rerun package:

```bash
python scripts/tools/analyze_stage3_failures_v1.py --summary-csv 05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/summary.csv --out-dir 05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1 --top-k 10
```

Core outputs:

- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/fail_profiles.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/class_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/dataset_fail_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/report.md`

Result/paper notes:

- `07_exports/results/RESULT_GR_STAGE3_FAIL_CLOSURE_V1.md`
- `06_writing/paper-gr-stage3-fail-closure-note-v1-en.md`
