# RESULT: GR + QM + Coupling Checkpoint v1

Date: 2026-03-04
Scope: execution checkpoint for GR/QM/coupling hardening (tooling + evidence refresh only)

## 1) Coupling Audit (v2) - bundled and validated

Per-block chunked audits (resume-safe) rechecked:

- primary `DS-002/003/006, seeds 3401..3600`: `600/600`
- attack `DS-002/003/006, seeds 3601..4100`: `1500/1500`
- holdout `DS-004/008, seeds 3401..3600`: `400/400`

Global coupling bundle (`05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/bundle-v1/`):

- `profiles_completed = 2500/2500`
- `g20_pass = 2500/2500`
- `gr_guard_pre_all_pass = true`
- `gr_guard_post_all_pass = true`
- `overall_decision = PASS`

## 2) GR Stage-3 status

Official remains:

- `597/600` pass (`gr-stage3-official-v3-rerun-v1`)
- remaining fails: `3` (all in `G11`)

Strict fail taxonomy + neighborhood diagnostics reconfirm:

- classes: `g11b_slope_instability`, `weak_corr_multi_peak`, `weak_corr_sparse_graph` (1 each)
- each fail anchor is isolated in `+/-5` seed window (`1/11`)

Interpretation:

- edge-case sensitivity, not broad local instability.

## 3) QM status

Stage-1:

- regression guard refreshed (`qm-stage1-regression-baseline-v1/latest_check`)
- taxonomy refreshed (`qm-stage1-failure-taxonomy-v1`)

Stage-2 (new strict taxonomy package):

- source: `qm-stage2-prereg-v1/*/qm_lane/summary.csv`
- total profiles: `2500`
- fail profiles: `750` (`30.0%`)
- dominant failing gate: `g17_status`
- top signatures: `g17_status`, `g18_status`, `g17_status+g18_status`

## 4) Anti post-hoc compliance

- no threshold changes
- no formula changes
- tooling + diagnostics + reproducibility updates only

## 5) Next actions

1. GR: candidate lane only if improvement on the 3 G11 signatures with `degraded=0`; otherwise keep known limitation.
2. QM Stage-2: focus candidate work on dominant gate (`G17`) first, then coupled `G18` signature.
3. Keep coupling bundle as fixed backbone while iterating candidates.
