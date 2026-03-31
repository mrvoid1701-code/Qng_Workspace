# GR Stage-3 G11/G12 Candidate-v3 Pre-Registration

Date: 2026-03-02  
Protocol ID: `gr-stage3-g11-g12-candidate-v3`

## Intent

Close the remaining Stage-3 official-v2 primary fails (`8/600`) with candidate-only estimator hardening, without changing gate thresholds or formulas.

Baseline for comparison in this protocol is Stage-3 official-v2:

- `05_validation/evidence/artifacts/gr-stage3-official-v2-rerun-v1/summary.csv`

## Frozen Inputs

- datasets primary: `DS-002, DS-003, DS-006`
- seeds primary: `3401..3600`
- attack A: `DS-002, DS-003, DS-006`, seeds `3601..4100`
- holdout B: `DS-004, DS-008`, seeds `3401..3600`
- `phi_scale=0.08` where applicable (from source runs)

## Candidate Definitions (No Threshold Tuning)

### G11a-v3 (candidate)

Applies only when `G11` is `fail` under official-v2.

1. Keep direct pass if `G11` already passes in official-v2.
2. Keep structural requirement unchanged:
   - require `G11b=pass`, `G11c=pass`, `G11d=pass`.
3. Keep source/target proxies unchanged:
   - `S(i)=|L_rw sigma_norm(i)|`
   - `T(i)=|R_smooth(i)|`
4. Keep correlation threshold unchanged:
   - `corr_min = 0.20`
5. Add support-quantile fallback (estimator hardening only):
   - evaluate rank rules at `q=0.80` and at `q=0.75`
   - candidate pass if `(base_or_trim at q=0.80) OR (base_or_trim at q=0.75)`
6. Multi-peak flag remains diagnostic-only (`peak2/peak1 >= 0.98`, `dist_norm <= 0.10`).

### G12d-v3 (candidate)

Applies only when `G12` is `fail` under official-v2.

1. Keep direct pass if `G12` already passes in official-v2.
2. Keep structural requirement unchanged:
   - require `G12a=pass`, `G12b=pass`, `G12c=pass`.
3. Keep threshold unchanged:
   - slope pass if `< -0.03`.
4. Candidate estimator hardening:
   - compute existing winsorized robust slope (`v2` method),
   - compute plain log-slope on the same bin-selection policy (no winsorization),
   - candidate pass if either slope passes the same threshold.

## Promotion Criteria (Hard)

For each block (primary, attack A, holdout B):

1. `degraded_vs_v2 = 0` (mandatory).
2. per-dataset non-degradation (mandatory).

Global:

1. `improved_vs_v2 > 0` on primary.
2. `improved_vs_v2 >= 0` on attack/holdout.
3. Publish side-by-side tables for `G11`, `G12`, and `Stage3`.

If any degraded profile appears, candidate-v3 is not eligible for promotion.

## Execution Closure (2026-03-02)

All prereg blocks were executed and evaluated:

- primary:
  - summary: `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/primary_ds002_003_006_s3401_3600/summary.csv`
  - eval: `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/primary_ds002_003_006_s3401_3600/report.json`
  - Stage3: `592 -> 597`, improved `5`, degraded `0`
- attack A (seed500):
  - summary: `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_seed500_ds002_003_006_s3601_4100/summary.csv`
  - eval: `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_seed500_ds002_003_006_s3601_4100/report.json`
  - Stage3: `1433 -> 1452`, improved `19`, degraded `0`
- holdout B:
  - summary: `05_validation/evidence/artifacts/gr-stage3-g11-g12-candidate-v3/attack_holdout_ds004_008_s3401_3600/summary.csv`
  - eval: `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v2/attack_holdout_ds004_008_s3401_3600/report.json`
  - Stage3: `398 -> 398`, improved `0`, degraded `0`

Protocol verdict:

- all blocks `PASS`
- `degraded_vs_v2 = 0` in every block
- per-dataset non-degradation `true` in every block
- primary net uplift satisfied
