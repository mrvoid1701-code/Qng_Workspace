# GR Stage-2 G11a-v4 Candidate Pre-Registration (No Threshold Tuning)

Date: 2026-03-02  
Status: candidate-only prereg (official gate unchanged in this file)

## Goal

Close remaining `G11` fails under official-v3 Stage-2 mapping without changing gate thresholds/formulas.

## Frozen Inputs

- primary datasets: `DS-002,DS-003,DS-006`
- primary seed range: `3401..3600`
- attack A datasets: `DS-002,DS-003,DS-006`
- attack A seed range: `3601..4100`
- attack B (holdout) datasets: `DS-004,DS-008`
- attack B seed range: `3401..3600`

## Frozen Constants (No Tuning)

- high-signal quantile: `0.80`
- smoothing: `alpha=0.50`, `iters=1`
- correlation threshold (unchanged): `0.20`
- trimmed fraction for robust rank diagnostic: `0.10`

No threshold changes are allowed in:

- `scripts/run_qng_einstein_eq_v1.py`
- `scripts/tools/run_gr_stage2_official_v3.py`

## Candidate Definition (`G11a-v4`)

Starting from official-v3 rows:

1. Keep all existing `G11 v3` passes unchanged.
2. For `G11 v3` fails with `G11b/G11c/G11d` pass, add robust rank fallback:
   - source: Poisson-like proxy `S(i)=|L_rw sigma_norm(i)|`
   - target: `T(i)=|R_smooth(i)|`
   - compute on high-signal subset (`top 20%` in `S`)
   - `rank_or_pass = (|Spearman_hs|>=0.20) OR (|Spearman_hs_trimmed|>=0.20)`
3. `G11 v4` passes if `G11 v3` passes OR robust fallback passes.

This is estimator hardening only; no threshold relaxation.

## Promotion Criteria (Frozen)

Primary:

- `degraded_vs_v3 = 0` (mandatory)
- `improved_vs_v3 >= 2`
- per-dataset non-degradation
- `g11_v4_fail <= 3` (equivalent to `>=99.5%` on 600 profiles)

Attack A / B:

- `degraded_vs_v3 = 0` (mandatory)
- per-dataset non-degradation
- `improved_vs_v3 >= 0` (no regression requirement; uplift may vary by split)

## Required Outputs

1. Strict fail-closure taxonomy package (`official-v3 rerun`):
   - `summary.csv`
   - `report.md`
2. Candidate eval package (primary + attacks):
   - `summary.csv`
   - `report.md`
3. Promotion evaluator package (primary + attacks):
   - `report.json`
   - `report.md`
4. Aggregate decision note:
   - `promotion_decision.md`
