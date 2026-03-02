# Changelog

## 2026-03-02 - GR Stage-2 prereg execution record (600 profiles)

- Executed frozen Stage-2 grid:
  - datasets: `DS-002/003/006`
  - seeds: `3401..3600`
  - profiles: `600`
- Added evidence package:
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/dataset_summary.csv`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/gr-stage2-prereg-v1/prereg_manifest.json`
- Updated protocol doc with execution record:
  - `docs/GR_STAGE2_PREREG.md`

## 2026-03-02 - GR Stage-2 prereg tooling + QM lane split

- Added GR Stage-2 prereg runner with one-summary CSV:
  - `scripts/tools/run_gr_stage2_prereg_v1.py`
- Added QM standalone lane runner:
  - `scripts/tools/run_qm_lane_check_v1.py`
- Added Stage-2 prereg doc:
  - `docs/GR_STAGE2_PREREG.md`
- Added QM lane separation policy:
  - `docs/QM_LANE_POLICY.md`
- Extended reproducibility command set:
  - `Makefile`
  - `docs/REPRODUCIBILITY.md`
- Updated gate/docs index pointers:
  - `docs/GATES.md`
  - `README.md`

## 2026-03-02 - GR Stage-1 internal freeze

- Added internal freeze page:
  - `docs/GR_STAGE1_FREEZE.md`
- Linked freeze page from repository index:
  - `README.md`
- Updated roadmap to reflect:
  - Stage-1 frozen scope
  - Stage-2 prereg as next GR expansion
  - QM lane separation until Stage-2 closure

## 2026-03-02 - GR status + one-command reproducibility + commitments freeze

- Added short GR status page:
  - `docs/GR_STATUS.md`
- Added frozen physics-facing scope contract:
  - `docs/GR_COMMITMENTS.md`
- Added one-command GR helper:
  - `scripts/tools/gr_one_command.py`
  - subcommands: `official-check`, `baseline-guard`, `sweep-phi`
- Added top-level `Makefile` targets:
  - `make gr_official_check DS=DS-003 SEED=3520`
  - `make gr_baseline_guard`
  - `make gr_sweep_phi`
- Updated reproducibility and repo index docs:
  - `docs/REPRODUCIBILITY.md`
  - `README.md`

## 2026-03-02 - G16b official switch to hybrid policy

- Added pre-switch safety tag:
  - `pre-g16b-hybrid-official`
- Promoted `G16b` official decision in:
  - `scripts/run_qng_action_v1.py`
  - policy: low-signal (`std(T11)/|mean(T11)| > 10`) uses `G16b-v2`; high-signal uses legacy `G16b-v1`
- Preserved audit rows in action metric artifacts:
  - `G16b` (official hybrid status)
  - `G16b-v1` (legacy)
  - `G16b-v2` (candidate component metrics)
- Updated compatibility readers:
  - `scripts/tools/run_g16b_v2_candidate_eval_v1.py`
  - `scripts/tools/run_g16_failure_taxonomy_v1.py`
  - `scripts/tools/run_g16b_split_hybrid_v1.py`
- Updated docs and logs:
  - `docs/GATES.md`
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`
  - `docs/G16B_HYBRID_PROMOTION_PREREG.md`
  - `docs/REPRODUCIBILITY.md`
  - `05_validation/results-log.md`
- Added smoke evidence package (`G13`, `G15`, `G16`):
  - `05_validation/evidence/artifacts/g16b-official-switch-smoke-v1/`

## 2026-03-02 - GR baseline/guard refresh after G16b switch

- Regenerated baseline source grid:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/run-log-grid20.txt`
  - grid definition: `DS-002/003/006 x seeds 3401..3420 x phi_scale=0.08`
- Rebuilt baseline JSONs with new effective tag:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json`
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
  - effective_tag: `gr-g16b-hybrid-official`
  - effective_commit: `077478d`
  - effective_date_utc: `2026-03-02`
- Reran regression guard against refreshed official baseline:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/`
  - result: `PASS`
  - source summary counts: `all_pass_official=53/60`, `all_pass_diagnostic=42/60`

## 2026-03-01 - G16b hybrid promotion prereg + attack validation

- Added promotion prereg doc:
  - `docs/G16B_HYBRID_PROMOTION_PREREG.md`
- Added promotion criteria evaluator:
  - `scripts/tools/evaluate_g16b_hybrid_promotion_v1.py`
- Added promotion/attack evidence outputs:
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/primary_ds002_003_006_s3401_3600/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_seed500_ds002_003_006_s3601_4100/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/attack_holdout_ds004_008_s3401_3600/`
  - `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/promotion_decision.md`
- Added attack-run summary artifacts:
  - `05_validation/evidence/artifacts/g16b-v2-candidate-attack-seed500-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-attack-holdout-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-attack-seed500-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-attack-holdout-v1/summary.csv`
- Outcome:
  - primary decision: `PASS`
  - attack seed-range decision: `PASS`
  - attack holdout decision: `PASS`
  - hybrid marked `PROMOTION-READY` (official gate switch still explicit/separate).

## 2026-03-01 - G16b hybrid split candidate prereg (low=v2, high=v1)

- Added hybrid evaluator:
  - `scripts/tools/run_g16b_split_hybrid_v1.py`
- Added evidence outputs:
  - `05_validation/evidence/artifacts/g16b-split-hybrid-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/prereg_manifest.json`
- Policy:
  - low-signal profiles use pre-registered `g16b_v2` decision
  - high-signal profiles keep legacy `g16b_v1` decision
- Result on DS-002/003/006 x seeds 3401..3600:
  - v1 fail `127/600`
  - hybrid fail `84/600`
  - improved `43`, degraded `0`
- Candidate passes prereg non-degradation checks and is marked as next promotion candidate (official gate unchanged).

## 2026-03-01 - G16b split protocol candidate (low/high signal) prereg eval

- Added split-protocol evaluator:
  - `scripts/tools/run_g16b_split_protocol_v1.py`
- Added sanity and prereg evidence:
  - `05_validation/evidence/artifacts/g16b-split-protocol-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/prereg_manifest.json`
- Frozen protocol:
  - signal index `p90(|T11|)`, threshold `0.024`
  - low gate: abs Pearson/Spearman + high-signal R2
  - high gate: abs Pearson + abs cosine + slope-only R2
- Result snapshot:
  - v1 fail `127/600`
  - split fail `100/600`
  - low-signal improved (`62 -> 20` fails), high-signal degraded (`65 -> 80` fails)
- Decision: split-v1 remains candidate-only; official G16b stays v1.

## 2026-03-01 - G16b-v2 candidate prereg evaluation (frozen)

- Added prereg evaluation runner:
  - `scripts/tools/run_g16b_v2_candidate_eval_v1.py`
- Added sanity and prereg evidence outputs:
  - `05_validation/evidence/artifacts/g16b-v2-candidate-sanity-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/summary.csv`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/report.md`
  - `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/prereg_manifest.json`
- Frozen protocol executed on `DS-002/003/006 x seeds 3401..3600` with `phi_scale=0.08` and strict prereg checks.
- Outcome:
  - `G16b-v1` fail `127/600`
  - `G16b-v2` fail `113/600`
  - v2 does not meet promotion rule (`600/600`), remains candidate-only.
- Updated proposal and reproducibility docs:
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`
  - `docs/REPRODUCIBILITY.md`

## 2026-03-01 - G16b component diagnostics expansion + candidate proposal

- Expanded G16 taxonomy diagnostics with per-profile G16b component outputs:
  - `mean/std` for `T11` and `G11`
  - `T11` sign fractions
  - `std(T11)/|mean(T11)|`
  - Pearson and Spearman correlations
  - high-signal subset diagnostics (top 20% `|T11|`)
- Added consolidated diagnostics CSV:
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16b_component_diagnostics.csv`
- Added A/B issue-axis mapping for failing profiles in taxonomy outputs.
- Added candidate-only proposal doc (no official gate switch):
  - `docs/G16B_DEFINITION_CHANGE_PROPOSAL.md`

## 2026-03-01 - G16 failure taxonomy diagnostics (no math changes)

- Added G16 taxonomy runner:
  - `scripts/tools/run_g16_failure_taxonomy_v1.py`
- Added taxonomy artifacts from grid20 profiles:
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_fail_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_pass_cases.csv`
  - `05_validation/evidence/artifacts/g16-failure-taxonomy-v1/g16_failure_taxonomy.md`
- Current result snapshot:
  - all observed G16 fails are `G16b`-driven (Einstein coupling R² sub-gate), with `G16a/G16c/G16d` passing.

## 2026-03-01 - GR baseline semantics split (official vs survey)

- Added explicit pass semantics in sweep/guard outputs:
  - `all_pass_official` (uses `G15b-v2`, excludes legacy-v1 effect)
  - `all_pass_diagnostic` (legacy chain including `G15` final)
- Added baseline modes in baseline builder:
  - `--mode survey` (full grid, including expected diagnostic fails)
  - `--mode official` (filtered pass-only official profiles)
- Added official baseline file:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`
- Guard default baseline now points to official baseline:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Updated tracked source summary with explicit official/diagnostic pass columns:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/summary.csv`

## 2026-03-01 - GR stability diagnostics (no math changes)

- Added diagnostics tool for G13/G14 drift stability from sweep summaries:
  - `scripts/tools/analyze_gr_stability_v1.py`
- Added baseline-derived outputs:
  - `05_validation/evidence/artifacts/gr-stability-v1/dataset_stats.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/worst_cases.csv`
  - `05_validation/evidence/artifacts/gr-stability-v1/report.md`
- Added reproducibility command for this diagnostics pass:
  - `docs/REPRODUCIBILITY.md`

## 2026-03-01 - GR regression guard deep baseline (grid20)

- Added deep baseline config (DS-002/003/006 x seeds 3401..3420, `PHI_SCALE=0.08`):
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_grid20.json`
- Added baseline builder helper:
  - `scripts/tools/build_gr_baseline_from_sweep.py`
- `gr_baseline_grid20.json` is now maintained as survey baseline (not pass-only official baseline).
- Added provenance source summary and run-log:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/source_runs_grid20/`

## 2026-03-01 - GR/PPN freeze: `gr-ppn-g15b-v2-official`

- Freeze scope: GR/PPN decision policy for G15b.
- Effective gate policy:
  - `G15b-v2` = official decision gate.
  - `G15b-v1` = legacy diagnostic-only gate.
- Promotion baseline commit: `15dd881`.
- Promotion rule source: `docs/G15B_DEFINITION_CHANGE_PROPOSAL.md`.
- Evidence baseline:
  - `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/`
  - `05_validation/evidence/artifacts/g15b-multipeak-diagnosis-v1/`

## 2026-03-01 - GR regression guard baseline (G10..G16)

- Added frozen guard baseline config:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline.json`
- Added automatic checker:
  - `scripts/run_qng_gr_regression_guard_v1.py`
- Added reproducibility command documentation:
  - `docs/REPRODUCIBILITY.md`
- Fixed `run_qng_phi_scale_sweep_v1.py` path handling for relative `--out-dir`.
