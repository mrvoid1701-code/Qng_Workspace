# GR Stage-3 Residual Failures in QNG: A Strict Diagnostic Closure Note (v1)

## Abstract

This note documents the residual failure structure of the current GR Stage-3 official policy in the QNG workspace. The official pass rate remains `597/600`, with `3/600` profiles failing. A strict fail-only taxonomy shows that all remaining failures are localized in `G11` (Einstein-equation closure proxy), with no residual `G12`, `G7`, `G8`, or `G9` failures in the remaining set. The three fail profiles split into three distinct mechanisms: slope instability, weak-correlation under multi-peak structure, and weak-correlation under sparse-graph structure. No thresholds or formulas were modified in this analysis; this is a diagnostic closure step to support anti post-hoc governance and a clean candidate-v5 preregistration.

## 1. Context

Current GR status in the repository:

- official policy: `gr-stage3-g11g12-v3-official`
- official rerun package: `05_validation/evidence/artifacts/gr-stage3-official-v3-rerun-v1/`
- result: `597/600` pass

The goal here is not to force `600/600` by threshold tuning, but to identify whether the residual failures are random noise or structured estimator failure modes.

## 2. Method

A strict fail taxonomy was executed on the official Stage-3 summary:

- input: `gr-stage3-official-v3-rerun-v1/summary.csv`
- analyzer: `scripts/tools/analyze_stage3_failures_v1.py`
- output package: `gr-stage3-official-v3-fail-closure-v1/`

Diagnostic policy:

1. classify only rows with `stage3_status=fail`,
2. map fail patterns by gate/subgate,
3. compute feature/fail correlations,
4. label likely fail causes by predefined regime signatures.

Additionally, nearest-pass neighbors were extracted per fail profile (same dataset, nearest seed distance) to test local sensitivity.

## 3. Results

### 3.1 Residual fail structure

- total residual fails: `3`
- fail pattern: `G11` only (`3/3`)
- cause classes:
  - `g11b_slope_instability` (`1`)
  - `weak_corr_multi_peak` (`1`)
  - `weak_corr_sparse_graph` (`1`)

### 3.2 Dataset distribution

Each of the three primary datasets contributes one fail:

- `DS-002`: 1 fail
- `DS-003`: 1 fail
- `DS-006`: 1 fail

This indicates a distributed edge-case structure, not concentration in a single dataset.

### 3.3 Local neighborhood behavior

For all three fail profiles, immediate seed neighbors (`|delta_seed| = 1`) in the same dataset pass the official Stage-3 decision. This supports an estimator-fragility interpretation (specific local regimes) rather than broad collapse of Stage-3 behavior.

## 4. Interpretation

The residual `3/600` are consistent with three different G11 edge signatures:

1. slope instability signature,
2. weak-correlation under multi-peak topology,
3. weak-correlation under sparse graph geometry.

This decomposition matters because it rejects the "single global fix" framing. A valid next step is a single conceptual candidate update (v5) that targets G11 robustness across these signatures without threshold relaxation.

## 5. Governance and Anti Post-Hoc Compliance

This note keeps anti post-hoc standards:

- no threshold changes,
- no formula changes,
- strict fail-only analysis on frozen official outputs,
- explicit separation of diagnostics vs promotion decisions.

Any promotion path to `600/600` must be preregistered and must satisfy:

1. `degraded=0` vs current official,
2. primary + attack + holdout checks,
3. explicit reporting of improvements on the current fail signatures.

## 6. Conclusion

GR Stage-3 remains strong and stable at `597/600`, with residual failures confined to three identifiable G11 mechanisms. The system is close to closure for an official paper trajectory, but the final step should be a controlled candidate-v5 estimator hardening cycle, not threshold tuning.

## 7. Data and Artifacts

- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/fail_profiles.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/class_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/pattern_summary.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/feature_correlations.csv`
- `05_validation/evidence/artifacts/gr-stage3-official-v3-fail-closure-v1/nearest_pass_neighbors.csv`

